import codecs

import pytest


class EncodingError(BaseException):
    pass


@pytest.fixture(scope="session")
def error_handler():
    def error_handler_raises(exception):
        raise EncodingError()

    codecs.register_error("raises", error_handler_raises)
