import json
import logging
from tempfile import TemporaryDirectory

import boto3


def get_raw_email(message_id: str, bucket_name: str, key_prefix: str) -> bytes:
    logger = logging.getLogger(__name__)
    s3_client = boto3.client('s3')

    with TemporaryDirectory() as tempdir:
        download_path = f'{tempdir}/{message_id}'
        logger.info('Downloading %s to %s', message_id, download_path)

        s3_client.download_file(bucket_name, f'{key_prefix}/{message_id}', download_path)

        with open(download_path, 'r+b') as f:
            return f.read()


def publish_to_sns(message: str, arn: str) -> None:
    logger = logging.getLogger(__name__)
    sns_client = boto3.client('sns')

    logger.info('Publishing message to %s', arn)
    response = sns_client.publish(
        TargetArn=arn,
        Message=json.dumps({'default': message}),
        MessageStructure='json'
    )

    logger.info('Published to "%s" as "%s"', arn, response['MessageId'])
