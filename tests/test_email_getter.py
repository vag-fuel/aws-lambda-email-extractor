from typing import Callable

import boto3
from moto import mock_s3
from pytest import fixture

from extractor.email_getter import get_raw_email


@fixture
def create_s3_object() -> Callable[[str, str, bytes], None]:
    def create_object(bucket: str, key: str, contents: bytes) -> None:
        client = boto3.client('s3')
        client.create_bucket(Bucket=bucket)
        client.put_object(Body=contents, Bucket=bucket, Key=key)

    with mock_s3():
        return create_object


@mock_s3
def test_that_get_raw_email_returns_files_from_s3(create_s3_object):
    bucket = 'some-bucket'
    prefix = 'foo-prefix'
    message_id = 'id1234'
    contents = b'hello world'
    create_s3_object(bucket, f'{prefix}/{message_id}', contents)

    assert get_raw_email(message_id, bucket, prefix) == contents
