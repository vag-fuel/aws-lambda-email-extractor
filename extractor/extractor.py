import email
import json
import logging

import boto3


# noinspection PyUnusedLocal
# pylint: disable=unused-argument
def lambda_handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    s3_client = boto3.client('s3')

    logger.info(json.dumps(event['Records'][0]['ses']))

    message_id = event['Records'][0]['ses']['mail']['messageId']
    object_key = f'dayton-freight/{message_id}'
    bucket_name = 'tank-levels'

    download_path = f'/tmp/{message_id}'

    logger.info('Fetching %s from %s to %s', object_key, bucket_name, download_path)
    s3_client.download_file(bucket_name, object_key, download_path)

    with open(download_path) as f:
        message = email.message_from_file(f)

    for part in message.walk():
        if part.get_content_disposition() == 'attachment':
            logger.info('Content Type: %s', part.get_content_type())
