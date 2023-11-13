import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.orm.query import Query
from sqlalchemy import func
from sqlalchemy.exc import OperationalError, ProgrammingError
from datetime import datetime, timedelta
from database.models import MindUsers, LessonCompletion
import logging
from typing import List


logger = logging.getLogger(__name__)


def get_active_users_query(session: Session) -> Query:
    """
    Simply returns the Query to fetch active users from Mindtickle Users

    Args:
        session: Session: SQLAlchemy session object

    Returns:
        A query object

    """
    active_users_query = (
        session.query(MindUsers.user_id, MindUsers.user_name)
        .filter(MindUsers.active_status == 'active')
    )

    return active_users_query


def get_lessons_completed_query(session: Session, active_users: List, start_date: datetime) -> Query:
    """
    The get_lessons_completed_query function returns a query that will return the number of lessons completed by each user
    in the active_users list on each day since start_date. The results are ordered by user id and completion date.

    Args:
        session: Session: SQLAlchemy session object
        active_users: List: List of active users (user ids) to filter the lessons completed table
        start_date: datetime: Start date to filter results from lessons completed table

    Returns:
        A query object

    """
    lessons_completed_query = (
            session.query(
                LessonCompletion.user_id,
                func.count(LessonCompletion.lesson_id).label('lessons_completed'),
                LessonCompletion.completion_date
            )
            .filter(
                LessonCompletion.user_id.in_(active_users),
                LessonCompletion.completion_date >= start_date,
                LessonCompletion.completion_date < datetime.now() - timedelta(days=1)  # Exclude today
            )
            .group_by(LessonCompletion.user_id, LessonCompletion.completion_date)
            .order_by(LessonCompletion.user_id, LessonCompletion.completion_date)
        )

    return lessons_completed_query


# This is the older function, that pulls all the data from active users in 1 go.
def generate_customer_x_report_v1(postgres_session: Session, mysql_session: Session) -> pd.DataFrame:
    """
    The function pulls filtered data from both databases and combines them into a single Dataframe.
    This function does it in a single go.

    Args:
        postgres_session: Session: Session object for PostgreSQL DB
        mysql_session: Session: Session object for MySQL DB

    Returns:
        The final dataframe with the desired data

    """
    active_users_statement = get_active_users_query(postgres_session).statement
    try:
        df_active_users = pd.read_sql(
            active_users_statement,
            postgres_session.bind
        )
    except OperationalError as e:
        logger.error(f'Failed to connect to the MindTickle Users DB. Details : ', exc_info=True)
        return pd.DataFrame()
    logging.debug('Pulled data from MindTickle Users successfully.')

    start_date = datetime.now() - timedelta(days=60)
    lessons_completed_query = get_lessons_completed_query(
        mysql_session,
        df_active_users['user_id'],
        start_date
    )

    try:
        df_lessons_completed = pd.read_sql(lessons_completed_query.statement, mysql_session.bind)
    except ProgrammingError as e:
        logger.error(f'Failed to pull data from Lessons Learned DB. Details : ', exc_info=True)
        return pd.DataFrame()
    logger.debug('Pulled data from Lessons Completed table successfully.')

    # Merge the two DataFrames on user_id
    final_df = pd.merge(df_active_users, df_lessons_completed, on='user_id', how='left')

    return final_df


def generate_customer_x_report(postgres_session: Session, mysql_session: Session) -> pd.DataFrame:
    """
    This is a modified version of the generate_customer_x_report to pull and process the data in chunks
    then concatenating the dataframes, rather than pulling and processing the data all at once.

    Args:
        postgres_session: Session: Session object for PostgreSQL DB
        mysql_session: Session: Session object for MySQL DB

    Returns:
        The final dataframe with the desired data

    """
    active_users_statement = get_active_users_query(postgres_session).statement
    try:
        df_active_users_chunks = pd.read_sql(
            active_users_statement,
            postgres_session.bind,
            chunksize=1000
        )
    except OperationalError as e:
        logger.error(f'Failed to connect to the MindTickle Users DB. Details :', exc_info=True)
        raise Exception

    logging.debug('Pulled data from MindTickle Users successfully.')

    start_date = datetime.now() - timedelta(days=60)

    df_list = []

    # We are fetching users in chunks above,
    # For each chunk, we are fetching the lessons that chunk of users have completed.
    # We then merge the dataframes on user_id
    # We save each merged dataframe in a list, and concat them finally.
    for df_active_users_part in df_active_users_chunks:
        lessons_completed_query = get_lessons_completed_query(
            mysql_session,
            df_active_users_part['user_id'],
            start_date
        )
        try:
            df_lessons_completed_chunk = pd.read_sql(
                lessons_completed_query.statement,
                mysql_session.bind
            )

            # Converting column type to int8 instead of int64 default to save some memory
            # The lessons completed column should never be too high
            # Because just how many lessons can a guy complete in a day?
            df_lessons_completed_chunk['lessons_completed'] = df_lessons_completed_chunk['lessons_completed'].astype('int8')
            part_df = pd.merge(df_active_users_part, df_lessons_completed_chunk, on='user_id', how='left')

            df_list.append(part_df)
        except ProgrammingError as e:
            logger.error(f'Failed to pull data from Lessons Completed DB. Details: ', exc_info=True)
            raise Exception

    final_df = pd.concat(df_list, ignore_index=True).sort_values('user_id', kind='mergesort')

    return final_df
