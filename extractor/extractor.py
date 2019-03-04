import logging
import os

from extractor.email_parser import ParsedEmail
from extractor.utils import publish_to_sns, get_raw_email


def lambda_handler(event: dict, _context):
    _configure_logging()

    transformer_arn = os.environ['TRANSFORMER_ARN']
    bucket_name = os.environ['EMAIL_BUCKET_NAME']

    message_id = event['Records'][0]['ses']['mail']['messageId']
    # key prefix is the first part of the email address (i.e. 'jdoe' from 'jdoe@example.com')
    key_prefix = event['Records'][0]['ses']['receipt']['recipients'][0].split('@')[0]

    raw_email = get_raw_email(message_id, bucket_name, key_prefix)
    message = ParsedEmail.from_bytes(raw_email)
    publish_to_sns(message.as_json(), transformer_arn)


def _configure_logging():
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)
    logging.basicConfig(level=logging.INFO)
