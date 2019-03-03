import boto3
from moto import mock_s3, mock_sns

from extractor.utils import get_raw_email, publish_to_sns


@mock_s3
def create_s3_object(bucket: str, key: str, contents: bytes) -> None:
    client = boto3.client('s3')
    client.create_bucket(Bucket=bucket)
    client.put_object(Body=contents, Bucket=bucket, Key=key)


@mock_sns
def create_sns_topic(name='test-topic') -> str:
    client = boto3.client('sns')
    topic = client.create_topic(Name=name)
    return topic['TopicArn']


@mock_s3
def test_that_get_raw_email_returns_files_from_s3():
    bucket = 'some-bucket'
    prefix = 'foo-prefix'
    message_id = 'id1234'
    contents = b'hello world'
    create_s3_object(bucket, f'{prefix}/{message_id}', contents)

    assert get_raw_email(message_id, bucket, prefix) == contents


@mock_sns
def test_that_publish_to_sns_works():
    arn = create_sns_topic()
    message = {'subject': 'foo', 'bar': 'baz'}
    message_id = publish_to_sns(message, arn)
    assert isinstance(message_id, str)
