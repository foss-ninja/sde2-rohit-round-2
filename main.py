import logging.config
import report
from report.report_types import ValidReports
import sys


logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)


def main(request_report: str) -> str:
    """
    The main function is the entry point for this Report Generation Script.

    Args:
        request_report: str: The type of report that is to be generated.

    Returns:
        A Pre-Signed Direct download link for the report.

    """
    download_link = report.generate_report(report_type=request_report)
    logger.debug('Report created and uploaded to S3.')
    return download_link


if __name__ == "__main__":
    total_args = len(sys.argv)
    # Checking if the there is only 1 cli argument passed
    # And if the passed argument is present in valid report types.
    # Else return the list of valid choices for report generation.

    valid_reports = set(report.value for report in ValidReports)

    # If there are no arguments passed, simply run the default report for which the script exists.
    if total_args == 1:
        print(main('customer_x'))

    elif (total_args != 2) or (sys.argv[1] not in valid_reports):
        print(f'Please enter a valid argument. Available report types -> {valid_reports}')
    else:
        print(main(sys.argv[1]))

