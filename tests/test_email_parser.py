import pathlib

from pytest import fixture

from extractor.email_parser import ParsedEmail


@fixture
def email_without_attachment() -> bytes:
    with open(pathlib.Path(__file__).parent / 'fixtures' / 'basic email.eml', 'r+b') as f:
        return f.read()


def test_that_email_message_can_read_an_email_without_attachments(email_without_attachment: bytes):
    message = ParsedEmail.from_bytes(email_without_attachment)

    assert message.from_addr == 'sender@example.com'
    assert message.to_addr == 'recipient@example.com'
    assert message.subject == 'Example Email'
    assert message.body == 'This is an example email\n*This is an example email*\nThis is an example email\n'
