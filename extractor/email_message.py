import email
import re


def clean_email_address(address: str) -> str:
    if '<' in address:
        match = re.search(r'<(.*?)>', address)
        if match:
            return match.group(1)
    return address


class EmailMessage:
    _to_addr: str
    _from_addr: str
    _subject: str
    _body: str

    def __init__(self, to_addr: str, from_addr: str, subject: str, body: str):
        super().__init__()
        self._to_addr = to_addr
        self._from_addr = from_addr
        self._subject = subject
        self._body = body

    @property
    def to_addr(self) -> str:
        return self._to_addr

    @property
    def from_addr(self) -> str:
        return self._from_addr

    @property
    def subject(self) -> str:
        return self._subject

    @property
    def body(self):
        return self._body

    @classmethod
    def from_bytes(cls, contents: bytes) -> 'EmailMessage':
        message = email.message_from_bytes(contents)
        return cls(
            clean_email_address(message['to']),
            clean_email_address(message['from']),
            message['subject'],
            message['body'])
