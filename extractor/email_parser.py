import email
import re
from base64 import b64decode
from typing import Tuple, Generator, Union


def clean_email_address(address: str) -> str:
    """Returns the bare email address when the address is something like 'John Doe <jdoe@example.com>'"""

    if '<' in address:
        match = re.search(r'<(.*?)>', address)
        if match:
            return match.group(1).strip()
    return address.strip()


class EmailAttachment:
    _attachment: email.message.EmailMessage

    def __init__(self, attachment: email.message.EmailMessage):
        self._attachment = attachment

    @property
    def body(self) -> Union[str, bytes]:
        body = self._attachment.get_payload()
        if self._attachment.get('Content-Transfer-Encoding') == 'base64':
            body = b64decode(body)
        if self.content_type == 'text/plain' and type(body) is bytes:
            body = body.decode()
        return body

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
    def body(self) -> str:
        # what if there is no plain text body? Consider using https://github.com/Alir3z4/html2text
        return self._message.get_body('plain').get_payload().replace('\r\n', '\n')

    @property
    def from_addr(self) -> str:
        return clean_email_address(self._message['from'])

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
