from database.models import ReportsGenerated
from exceptions.report_gen_exceptions import DataSaveFailure
from sqlalchemy.orm import Session
from typing import Dict
import logging
import sys

# Because SQLAlchemy tracebacks are super long, and generally not helpful.
# They will pollute the otherwise clean error logs.
# This will still give us the main error, just no traceback.
sys.tracebacklimit = 0


logger = logging.getLogger(__name__)


def save_to_db(session: Session, report_attributes: Dict, download_link: str) -> bool:
    """
    The save_to_db function accepts all attributes of the Report, along with the
    direct download link and saves it all in the DB.

    Args:
        report_attributes: Dict: All details about the report.
        download_link: str: Download link to be saved for the report in DB.
        session: Session: A SqlAlchemy session object.

    Returns:
        True if data saving goes smoothly.
    """
    report_attributes['download_link'] = download_link

    try:
        session.add(ReportsGenerated(**report_attributes))
        session.commit()
    # Catching any DB errors while trying to write the report details.
    except Exception as e:
        logger.exception(f'Failed to save report details to the DB. Details : {str(e)}')
        raise DataSaveFailure('Failed to save report details to the DB.')
    else:
        logger.debug(f'Report details saved to the DB.\nReport ID: {report_attributes["report_id"]}')
    finally:
        session.close()
    return True
