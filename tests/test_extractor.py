import botocore
import json
import os
from botocore.client import BaseClient
from moto import mock_s3
from pytest import fixture
from typing import Callable, List, Tuple, Union

from extractor.email_parser import ParsedEmail
from extractor.extractor import lambda_handler
from .utils import create_s3_object


@fixture
def set_environment_variable():
    old_values: List[Tuple[str, Union[str, None]]] = []

    def set_env_var(name: str, value: str) -> None:
        old_values.append((name, os.environ.get(value)))
        os.environ[name] = value
    yield set_env_var

    for var_name, old_value in old_values:
        if old_value is None:
            del os.environ[var_name]
        else:
            os.environ[var_name] = old_value


@mock_s3
def test_that_lambda_handler_wires_everything_correctly(
        base_email: bytes,
        mock_sns_client: botocore.client.BaseClient,
        set_environment_variable: Callable[[str, str], None]):
    sns_arn = 'I am an ARM'
    bucket = 'bucket-bucket-bucket'
    prefix = 'tank-recipient'
    message_id = 'id1234'

    set_environment_variable('TRANSFORMER_ARN', sns_arn)
    set_environment_variable('EMAIL_BUCKET_NAME', bucket)
    create_s3_object(bucket, f'{prefix}/{message_id}', base_email)

    event = {
        'Records': [
            {
                'ses': {
                    'mail': {'messageId': message_id},
                    'receipt': {
                        'recipients': [f'{prefix}@foo.com'],
                    },
                },
            },
        ],
    }

    lambda_handler(event, None)
    mock_sns_client.publish.assert_called_once_with(
        TargetArn=sns_arn,
        Message=json.dumps({'default': ParsedEmail.from_bytes(base_email).as_json()}),
        MessageStructure='json')
