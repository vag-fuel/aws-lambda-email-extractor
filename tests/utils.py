import boto3
from moto import mock_s3


@mock_s3
def create_s3_object(bucket: str, key: str, contents: bytes) -> None:
    client = boto3.client('s3')
    client.create_bucket(Bucket=bucket)
    client.put_object(Body=contents, Bucket=bucket, Key=key)
