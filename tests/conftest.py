import pathlib
from pytest import fixture


@fixture
def base_email() -> bytes:
    with open(pathlib.Path(__file__).parent / 'fixtures' / 'basic email.eml', 'r+b') as f:
        return f.read()
