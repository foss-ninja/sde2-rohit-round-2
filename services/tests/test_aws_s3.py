import unittest
from unittest.mock import patch
from moto import mock_s3
import boto3
from services.aws_s3 import upload_to_s3, create_s3_client, get_s3_download_link


class TestUploadToS3(unittest.TestCase):
    @mock_s3
    def test_upload_to_s3(self):
        # Set up a mock S3 bucket
        bucket_name = "test-bucket"
        object_key = "test-file.txt"
        region_name = "ap-south-1"
        metadata = {"key1": "value1", "key2": "value2"}

        # Create the mock S3 bucket with the correct region
        conn = boto3.resource("s3", region_name=region_name)
        conn.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': region_name})

        file_content = "Test file content"

        download_link = upload_to_s3(conn.meta.client, file_content, bucket_name, object_key, metadata)

        print(download_link)
        # Assertions
        self.assertTrue(download_link.startswith(f"https://{bucket_name}.s3.amazonaws.com/{object_key}"))

        # Optional: Check if the object is actually present in the S3 bucket
        obj = conn.Object(bucket_name, object_key)
        uploaded_content = obj.get()["Body"].read().decode("utf-8")
        self.assertEqual(uploaded_content, file_content)


class TestGetS3DownloadLink(unittest.TestCase):
    @patch('services.aws_s3.boto3.client')
    def test_get_s3_download_link(self, mock_boto_client):
        # Mock the S3 client
        mock_s3_client = mock_boto_client.return_value

        # Mock the URL generation
        mock_s3_client.generate_presigned_url.return_value = 'mocked_download_link'

        # Call the function
        download_link = get_s3_download_link(mock_s3_client, 'test-bucket', 'test-file.txt')

        # Assertions
        mock_s3_client.generate_presigned_url.assert_called_with(
            'get_object',
            Params={
                'Bucket': 'test-bucket',
                'Key': 'test-file.txt'
            },
            ExpiresIn=unittest.mock.ANY  # You may want to check for a specific expiration time
        )

        self.assertEqual(download_link, 'mocked_download_link')


if __name__ == '__main__':
    unittest.main()
