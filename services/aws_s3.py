import boto3
import logging
from config import settings
from typing import Dict
from botocore.exceptions import (
    ParamValidationError,
    ClientError
)
import botocore
from exceptions.report_gen_exceptions import (
    UploadFailure,
    S3ClientCreationError
)


logger = logging.getLogger(__name__)


def save(file_to_upload: str, bucket_name: str, object_key: str, metadata: Dict) -> str:
    """
    The save function calls the s3 client creation, and then calls the upload function.

    Args:
        file_to_upload: str: File as a string object.
        bucket_name: str: S3 Bucket name where the file will be uploaded.
        object_key: str: File name to be uploaded.
        metadata: Dict: Metadata for the s3 object.

    Returns:
        A pre-signed direct download link for the uploaded file.
    """
    s3_client = create_s3_client()
    download_link = upload_to_s3(s3_client, file_to_upload, bucket_name, object_key, metadata)
    return download_link


# TODO: This is not the best way to connect to AWS services (using the access_key and key_id)
# But this is the only setup I have ATM on my local machine.
# If using AWS IAM role that are preconfigured, the function will remain mostly the same,
# just without the `aws_access_key_id` and `aws_secret_access_key` parameters.
def create_s3_client():
    """
    Simply creates a new S3 client instance.

    Returns:
        An s3 client instance based on the environment variables passed.
    """
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            config=boto3.session.Config(
                s3={'addressing_style': 'path'},
                signature_version='s3v4'
            ),
            region_name=settings.region_name
        )
    except ClientError as e:
        logger.error(f'Failed to create a S3 instance. Details: {str(e)}')
        raise S3ClientCreationError(f'Failed to upload the file to S3. Details: {str(e)}')
    except botocore.exceptions.EndpointConnectionError as e:
        logger.error(f'Failed to connect to S3. Details: {str(e)}')
        raise S3ClientCreationError(f'Failed to Connect to S3. Details: {str(e)}\nVery likely that the region is wrong.')
    else:
        return s3


def upload_to_s3(
        s3_client: boto3.client,
        file_to_upload: str,
        bucket_name: str,
        object_key: str,
        metadata: Dict
) -> str:
    """
    The upload_to_s3 function uploads a file to an S3 bucket.

    Args:
        s3_client: boto3.client: The boto3 client where the file needs to be uploaded.
        file_to_upload: str: File as a string object.
        bucket_name: str: S3 Bucket name where the file will be uploaded.
        object_key: str: File name to be uploaded.
        metadata: Dict: Metadata for the s3 object.

    Returns:
        A pre-signed direct download link for the uploaded file.
    """
    # Create a new S3 Client.
    # s3_client = create_s3_client()

    # Try to upload the file in the specified S3.
    # If any of the Parameters passed cause an error, it will be caught by the ParamValidationError.
    # If the Bucket name is wrong, it will be caught as ClientError.
    try:
        s3_client.put_object(
            Body=file_to_upload,
            Bucket=bucket_name,
            Key=object_key,
            Metadata=metadata
        )
        logger.debug(f"Report uploaded to S3: s3://{bucket_name}/{object_key}")
    except ClientError as e:
        logger.error(f'Failed to connect to the S3 bucket. Details: {str(e)}')
        raise UploadFailure(f'Failed to upload the file to S3. Details: {str(e)}')
    except ParamValidationError as e:
        logger.exception(f'Upload to AWS failed because of invalid Parameters passed.\nDetails: {str(e)}')
        raise UploadFailure(f'Upload to AWS failed, because invalid Parameters were passed.\nDetails: {str(e)}')
    else:
        # Generate a direct download link for the uploaded report.
        download_link = get_s3_download_link(s3_client, bucket_name, object_key)
        return download_link


def get_s3_download_link(s3_client: boto3.client, bucket_name: str, object_key: str, expires_in: int = 60000) -> str:
    """
    The get_s3_download_link function generates a pre-signed direct download link for an Object on S3.

    Args:
        s3_client: boto3.client: A Boto3 S3 client, from which to download the file.
        bucket_name: str: S3 bucket where the file is present.
        object_key: str: Filename of the file for which the link will be generated.
        expires_in: int: Validity of the link. Default = 60000.

    Returns:
        A pre-signed direct download url for the requested file.
    """
    url = s3_client.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': bucket_name,
            'Key': object_key
        },
        ExpiresIn=expires_in
    )

    return url
