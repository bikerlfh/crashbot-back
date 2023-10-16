# Standard Library
import logging

# Libraries
import boto3

logger = logging.getLogger(__name__)


def upload_file_to_s3(*, file_path: str, bucket_name: str, key: str) -> bool:
    """
    Uploads a file to S3
    @param file_path: The path of the file to upload
    @param bucket_name: The name of the bucket
    @param key: The key of the file
    """
    s3_client = boto3.client("s3")
    try:
        s3_client.upload_file(file_path, bucket_name, key)
        logger.info("upload_file_to_s3 :: " "File uploaded successfully to S3")
        return True
    except FileNotFoundError:
        logger.error(f"upload_file_to_s3 :: file {file_path} not found")
    except Exception as e:
        logger.exception(f"upload_file_to_s3 :: {str(e)}")
    return False


# create a function to download a file from s3
def download_file_from_s3(
    *, bucket_name: str, key: str, file_path: str
) -> bool:
    """
    Downloads a file from S3
    @param bucket_name: The name of the bucket
    @param key: The key of the file
    @param file_path: The path to download the file to
    """
    s3_client = boto3.client("s3")
    try:
        s3_client.download_file(bucket_name, key, file_path)
        logger.info(
            "download_file_from_s3 :: " "File downloaded successfully from S3"
        )
        return True
    except FileNotFoundError:
        logger.error(
            f"download_file_from_s3 :: " f"file {file_path} not found"
        )
    except Exception as e:
        logger.exception(f"download_file_from_s3 :: {str(e)}")
    return False


def delete_file_from_s3(*, bucket_name: str, key: str) -> bool:
    """
    Deletes a file from S3
    @param bucket_name: The name of the bucket
    @param key: The key of the file
    """
    s3_client = boto3.client("s3")
    try:
        s3_client.delete_object(Bucket=bucket_name, Key=key)
        logger.info(
            "delete_file_from_s3 :: " "File deleted successfully from S3"
        )
        return True
    except FileNotFoundError:
        logger.error(f"delete_file_from_s3 :: file {key} not found")
    except Exception as e:
        logger.exception(f"delete_file_from_s3 :: {str(e)}")
    return False
