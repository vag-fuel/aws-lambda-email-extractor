import pathlib
from base64 import b64encode

from pytest import fixture

from extractor.email_parser import ParsedEmail


@fixture
def base_email() -> bytes:
    with open(pathlib.Path(__file__).parent / 'fixtures' / 'basic email.eml', 'r+b') as f:
        return f.read()


@fixture
def html_email() -> bytes:
    with open(pathlib.Path(__file__).parent / 'fixtures' / 'html email.eml', 'r+b') as f:
        return f.read()


@fixture
def two_recipient_email() -> bytes:
    with open(pathlib.Path(__file__).parent / 'fixtures' / 'email with two recipients.eml', 'r+b') as f:
        return f.read()


@fixture
def email_with_attachments() -> bytes:
    with open(pathlib.Path(__file__).parent / 'fixtures' / 'email with attachments.eml', 'r+b') as f:
        return f.read()


def test_that_email_message_can_read_an_email_without_attachments(base_email: bytes):
    message = ParsedEmail.from_bytes(base_email)

    assert message.from_addr == 'sender@example.com'
    assert message.to_addr == ('recipient@example.com',)
    assert message.subject == 'Example Email'
    assert message.body == 'This is an example email\n*This is an example email*\nThis is an example email\n'


def test_that_html_emails_are_converted_to_plain_text(html_email: bytes):
    message = ParsedEmail.from_bytes(html_email)

    assert message.body == 'This is an example email\n\n **This is an example email**\n\nThis is an example email'


def test_to_addr_contains_all_email_recipients(two_recipient_email: bytes):
    message = ParsedEmail.from_bytes(two_recipient_email)

    assert message.to_addr == ('recipient@example.com', 'foo@example.com')


def test_that_attachments_are_extracted(email_with_attachments: bytes):
    message = ParsedEmail.from_bytes(email_with_attachments)
    attachments = list(message.get_attachments())

    assert message.has_attachments
    assert len(attachments) == 3
    assert attachments[0].filename == 'a-text-file.txt'
    assert attachments[1].filename == 'a-pdf-file.pdf'
    assert attachments[2].filename == 'an-excel-file.xlsx'


def test_that_attachments_get_decoded(email_with_attachments: bytes):
    message = ParsedEmail.from_bytes(email_with_attachments)

    text_file = list(message.get_attachments())[0]
    pdf_file = list(message.get_attachments())[1]
    excel_file = list(message.get_attachments())[2]

    assert text_file.filename == 'a-text-file.txt'
    assert text_file.body == b'This is a text file\n'

    assert pdf_file.filename == 'a-pdf-file.pdf'
    assert pdf_file.body.startswith(b'%PDF-1.4\n%\xc7\xec\x8f\xa2\n5')

    assert excel_file.filename == 'an-excel-file.xlsx'
    assert excel_file.body.startswith(b'PK\x03\x04\x14\x00\x00\x00\x08\x00\xc5\xa5RN')


def test_that_as_dict_works(email_with_attachments: bytes):
    message = ParsedEmail.from_bytes(email_with_attachments)
    attachments = list(message.get_attachments())

    expected = {
        'from': 'sender@example.com',
        'to': ['dayton-freight@tanks.vagfuel-oil.com'],
        'subject': 'An email with attachments',
        'body': 'This is the message body\n',
        'attachments': [
            {
                'filename': 'a-text-file.txt',
                'content-type': 'text/plain',
                'body': b64encode(attachments[0].body).decode(),
                'base64': True,
            },
            {
                'filename': 'a-pdf-file.pdf',
                'content-type': 'application/pdf',
                'body': b64encode(attachments[1].body).decode(),
                'base64': True,
            },
            {
                'filename': 'an-excel-file.xlsx',
                'content-type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'body': b64encode(attachments[2].body).decode(),
                'base64': True,
            }
        ]
    }

    assert message.as_dict() == expected
