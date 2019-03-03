import json
import logging
from tempfile import TemporaryDirectory

import boto3
from typing import Dict


def get_raw_email(message_id: str, bucket_name: str, key_prefix: str) -> bytes:
    logger = logging.getLogger(__name__)
    s3_client = boto3.client('s3')

    with TemporaryDirectory() as tempdir:
        download_path = f'{tempdir}/{message_id}'
        logger.info('Downloading %s to %s', message_id, download_path)

        s3_client.download_file(bucket_name, f'{key_prefix}/{message_id}', download_path)

        with open(download_path, 'r+b') as f:
            return f.read()


def publish_to_sns(message: Dict, arn: str) -> str:
    logger = logging.getLogger(__name__)
    sns_client = boto3.client('sns')

    logger.info('Publishing message "%s" to %s', message['subject'], arn)
    response = sns_client.publish(
        TargetArn=arn,
        Message=json.dumps({'default': json.dumps(message)}),
        MessageStructure='json'
    )

    logger.info('Published "%s" as %s', message['subject'], response['MessageId'])
    return response['MessageId']
