import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date
from report.customer_x_report import generate_customer_x_report
import pandas as pd
from database.connections import POSTGRES_DB_URL, MYSQL_DB_URL


@pytest.fixture
def postgres_session():
    engine = create_engine(POSTGRES_DB_URL)
    SessionClass = sessionmaker(bind=engine)
    session = SessionClass()
    return session


@pytest.fixture
def mysql_session():
    engine = create_engine(MYSQL_DB_URL)
    SessionClass = sessionmaker(bind=engine)
    session = SessionClass()
    return session


def test_generate_customer_x_report(postgres_session, mysql_session):
    result_df = generate_customer_x_report(postgres_session, mysql_session)

    expected_result = pd.DataFrame().from_dict({'user_id': {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 3, 7: 3, 8: 3, 9: 3, 10: 3, 11: 3, 12: 4, 13: 4, 14: 4, 15: 4, 16: 4, 17: 4, 18: 4}, 'user_name': {0: 'User1', 1: 'User1', 2: 'User1', 3: 'User1', 4: 'User1', 5: 'User1', 6: 'User3', 7: 'User3', 8: 'User3', 9: 'User3', 10: 'User3', 11: 'User3', 12: 'User4', 13: 'User4', 14: 'User4', 15: 'User4', 16: 'User4', 17: 'User4', 18: 'User4'}, 'lessons_completed': {0: 2, 1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2, 9: 2, 10: 2, 11: 2, 12: 2, 13: 2, 14: 2, 15: 2, 16: 2, 17: 2, 18: 2}, 'completion_date': {0: date(2023, 9, 16), 1: date(2023, 9, 18), 2: date(2023, 9, 19), 3: date(2023, 9, 20), 4: date(2023, 9, 21), 5: date(2023, 9, 22), 6: date(2023, 9, 15), 7: date(2023, 9, 16), 8: date(2023, 9, 18), 9: date(2023, 9, 19), 10: date(2023, 9, 20), 11: date(2023, 9, 22), 12: date(2023, 9, 15), 13: date(2023, 9, 16), 14: date(2023, 9, 18), 15: date(2023, 9, 19), 16: date(2023, 9, 20), 17: date(2023, 9, 21), 18: date(2023, 9, 22)}})

    pd.testing.assert_frame_equal(result_df, expected_result, check_dtype=False)
