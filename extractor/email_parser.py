import email
import re


def clean_email_address(address: str) -> str:
    """Returns the bare email address when the address is something like 'John Doe <jdoe@example.com>'"""

    if '<' in address:
        match = re.search(r'<(.*?)>', address)
        if match:
            return match.group(1)
    return address


class ParsedEmail:
    _message: email.message.EmailMessage

    def __init__(self, message: email.message.EmailMessage):
        super().__init__()
        self._message = message

    @property
    def to_addr(self) -> str:
        return clean_email_address(self._message['to'])

    @property
    def from_addr(self) -> str:
        return clean_email_address(self._message['from'])

    @property
    def subject(self) -> str:
        return self._message['subject']

    @property
    def body(self) -> str:
        # what if there is no plain text body? Consider using https://github.com/Alir3z4/html2text
        return self._message.get_body('plain').get_payload().replace('\r\n', '\n')

    @classmethod
    def from_bytes(cls, contents: bytes) -> 'ParsedEmail':
        return cls(email.message_from_bytes(contents, _class=email.message.EmailMessage))
