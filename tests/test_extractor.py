import boto3
import botocore
import json
import os
from botocore.client import BaseClient
from mock import MagicMock
from moto import mock_s3
from pytest import fixture
from typing import Callable, List, Tuple, Union

from email_parser import ParsedEmail
from extractor.extractor import lambda_handler
from.utils import create_s3_object


@fixture
def mock_sns_client(mocker) -> botocore.client.BaseClient:
    real_client_factory = boto3.client
    mock_client = MagicMock()

    def factory_factory(client_type: str):
        return mock_client if client_type == 'sns' else real_client_factory(client_type)

    mocker.patch.object(boto3, 'client', side_effect=factory_factory)

    return mock_client


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
    set_environment_variable('TRANSFORMER_ARN', sns_arn)

    bucket = 'tank-levels'
    prefix = 'tank-recipient'
    message_id = 'id1234'
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
        Message=json.dumps({'default': json.dumps(ParsedEmail.from_bytes(base_email).as_dict())}),
        MessageStructure='json')
