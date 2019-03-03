import logging

from extractor.email_parser import ParsedEmail
from extractor.email_getter import get_raw_email


def lambda_handler(event: dict, _context):
    _configure_logging()
    logger = logging.getLogger(__name__)

    message_id = event['Records'][0]['ses']['mail']['messageId']
    bucket_name = 'tank-levels'
    # key prefix is the first part of the email address (i.e. 'jdoe' from 'jdoe@example.com')
    key_prefix = event['Records'][0]['ses']['receipt']['recipients'][0].split('@')[0]

    raw_email = get_raw_email(message_id, bucket_name, key_prefix)
    message = ParsedEmail.from_bytes(raw_email)

    # do something with the message
    logger.info('%s %s %s', message.from_addr, ', '.join(message.to_addr), message.body)


def _configure_logging():
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)
    logging.basicConfig(level=logging.DEBUG)
