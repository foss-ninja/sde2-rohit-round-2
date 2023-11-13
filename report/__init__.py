from database.connections import PostgresSession, MysqlSession
from .customer_x_report import generate_customer_x_report
from .report_types import ValidReports
from services.aws_s3 import save
from services.save_report_details import save_to_db
from config import settings
from exceptions.report_gen_exceptions import DataFetchError
from datetime import date
from uuid import uuid4
import logging
import pandas as pd


logger = logging.getLogger(__name__)


def generate_report(report_type: str) -> str:

    """
    The generate_report function is responsible for generating a variety of reports.
    Current functionality includes the following report types:
    - customer_x

    Args:
        report_type: str: Determine which report to generate

    Returns:
        A Download Link for the Report.

    """
    s3_bucket_name = settings.s3_bucket_name
    s3_object_key = f"{report_type}_report/{date.today()}.csv"
    metadata = {
                'report_id': str(uuid4()),
                's3_object_key': s3_object_key,
                's3_bucket': s3_bucket_name,
                'report_date': str(date.today()),
                'report_type': report_type
            }
    final_dataframe = pd.DataFrame()

    # This function will simply call different generate_x_report methods based on the argument that was passed.
    # Rest of the function will be the same.

    if report_type == ValidReports.CUSTOMER_X.value:
        with PostgresSession() as postgres_session, MysqlSession() as mysql_session:
            final_dataframe = generate_customer_x_report(postgres_session, mysql_session)

    if final_dataframe.empty:
        logger.exception('Failed to Pull the data.')
        raise DataFetchError('Failed to Pull data to build the report!')

    csv_data = final_dataframe.to_csv(index=False)

    download_link = save(csv_data, s3_bucket_name, s3_object_key, metadata)
    postgres_session = PostgresSession()
    saved = save_to_db(postgres_session, metadata, download_link)

    return download_link

