import boto3
import json
from mock import MagicMock
from moto import mock_s3

from extractor.utils import get_raw_email, publish_to_sns
from .utils import create_s3_object


@mock_s3
def test_that_get_raw_email_returns_files_from_s3():
    bucket = 'some-bucket'
    prefix = 'foo-prefix'
    message_id = 'id1234'
    contents = b'hello world'
    create_s3_object(bucket, f'{prefix}/{message_id}', contents)

    assert get_raw_email(message_id, bucket, prefix) == contents


def test_that_publish_to_sns_works(mocker):
    arn = 'I am an SNS topic'
    mock_client = MagicMock()
    mocker.patch.object(boto3, 'client', return_value=mock_client)

    message = json.dumps({'subject': 'foo', 'bar': 'baz'})
    publish_to_sns(message, arn)
    mock_client.publish.assert_called_with(
        TargetArn=arn,
        Message=json.dumps({'default': message}),
        MessageStructure='json')
