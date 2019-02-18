import pathlib

from pytest import fixture

from extractor.email_message import EmailMessage


@fixture
def email_without_attachment() -> bytes:
    with open(pathlib.Path(__file__).parent / 'fixtures' / 'email without attachment.eml', 'r+b') as f:
        return f.read()


def test_that_email_message_can_read_an_email_without_attachments(email_without_attachment: bytes):
    message = EmailMessage.from_bytes(email_without_attachment)

    assert message.from_addr == 'sender@example.com'
    assert message.to_addr == 'recipient@example.com'
    assert message.subject == 'Example Email'
