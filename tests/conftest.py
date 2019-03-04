import boto3
import botocore
import pathlib
from botocore.client import BaseClient
from mock import MagicMock
from pytest import fixture


@fixture
def base_email() -> bytes:
    with open(pathlib.Path(__file__).parent / 'fixtures' / 'basic email.eml', 'r+b') as f:
        return f.read()


@fixture
def mock_sns_client(mocker) -> botocore.client.BaseClient:
    real_client_factory = boto3.client
    mock_client = MagicMock()

    def factory_factory(client_type: str):
        return mock_client if client_type == 'sns' else real_client_factory(client_type)

    mocker.patch.object(boto3, 'client', side_effect=factory_factory)

    return mock_client
