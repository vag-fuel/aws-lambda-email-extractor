import logging
from tempfile import TemporaryDirectory

import boto3


def get_raw_email(message_id: str, bucket_name: str, key_prefix: str) -> bytes:
    """Gets the raw email from s3"""

    logger = logging.getLogger(__name__)
    s3_client = boto3.client('s3')

    with TemporaryDirectory() as tempdir:
        download_path = f'{tempdir}/{message_id}'
        logger.info('Downloading %s to %s', message_id, download_path)

        s3_client.download_file(bucket_name, f'{key_prefix}/{message_id}', download_path)

        with open(download_path, 'r+b') as f:
            return f.read()
