import email
import logging
import re
from typing import Tuple, Generator, Union

from html2text import html2text


LOGGER = logging.getLogger(__name__)


def clean_email_address(address: str) -> str:
    """Returns the bare email address when the address is something like 'John Doe <jdoe@example.com>'"""

    if '<' in address:
        match = re.search(r'<(.*?)>', address)
        if match:
            return match.group(1).strip()
        else:
            LOGGER.warning('Unable to clean email address "%s" even though it contains "<"', address)
    return address.strip()


class EmailAttachment:
    _attachment: email.message.EmailMessage

    def __init__(self, attachment: email.message.EmailMessage):
        self._attachment = attachment

    @property
    def body(self) -> bytes:
        return self._attachment.get_payload(decode=True)

    @property
    def content_type(self) -> str:
        return self._attachment.get_content_type()

    @property
    def filename(self) -> str:
        return self._attachment.get_filename()


class ParsedEmail:
    _message: email.message.EmailMessage

    def __init__(self, message: email.message.EmailMessage):
        super().__init__()
        self._message = message

    @property
    def body(self) -> Union[str, None]:
        body = None
        body_part = self._message.get_body(('plain', 'related', 'html'))
        if body_part:
            if body_part.get_content_type() == 'text/html':
                body = html2text(body_part.get_payload()).strip()
            else:
                body = body_part.get_payload().replace('\r', '')
        return body

    @property
    def from_addr(self) -> str:
        return clean_email_address(self._message['from'])

    @property
    def has_attachments(self) -> bool:
        for _ in self.get_attachments():
            return True
        return False

    @property
    def subject(self) -> str:
        return self._message['subject']

    @property
    def to_addr(self) -> Tuple[str]:
        return tuple([clean_email_address(to) for to in self._message['to'].split(',')])

    def get_attachments(self) -> Generator[EmailAttachment, None, None]:
        # I'd love to just use iter_attachments() here, but it was throwing exceptions
        for part in self._message.walk():
            if part.get_content_disposition() == 'attachment':
                yield EmailAttachment(part)

    @classmethod
    def from_bytes(cls, contents: bytes) -> 'ParsedEmail':
        return cls(email.message_from_bytes(contents, _class=email.message.EmailMessage))
