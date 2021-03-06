import email
import json
import logging
import re
from base64 import b64encode
from typing import Tuple, Generator, Union, Dict, List

from html2text import html2text


def clean_email_address(address: str) -> str:
    """Returns the bare email address when the address is something like 'John Doe <jdoe@example.com>'"""

    logger = logging.getLogger(__name__)

    if '<' in address:
        match = re.search(r'<(.*?)>', address)
        if match:
            return match.group(1).strip()
        else:
            logger.warning('Unable to clean email address "%s" even though it contains "<"', address)
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

    def as_dict(self) -> Dict[str, str]:
        return {
            'filename': self.filename,
            'content-type': self.content_type,
            'body': b64encode(self.body).decode(),
            'base64': True,
        }


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

    def as_dict(self) -> Dict[str, Union[str, List[str], Dict[str, Union[str, bool]]]]:
        return {
            'from': self.from_addr,
            'to': list(self.to_addr),
            'subject': self.subject,
            'body': self.body,
            'attachments': [attachment.as_dict() for attachment in self.get_attachments()],
        }

    def as_json(self) -> str:
        return json.dumps(self.as_dict())

    @classmethod
    def from_bytes(cls, contents: bytes) -> 'ParsedEmail':
        return cls(email.message_from_bytes(contents, _class=email.message.EmailMessage))
