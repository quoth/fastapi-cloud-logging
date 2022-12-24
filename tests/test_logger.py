from logging import Logger

import pytest
from pytest_mock import MockerFixture

from fastapi_cloud_logging.fastapi_cloud_logging_handler import FastAPILoggingHandler


@pytest.fixture
def logging_handler(mocker: MockerFixture) -> FastAPILoggingHandler:
    return FastAPILoggingHandler(
        mocker.Mock(), transport=mocker.Mock(), structured=True
    )


@pytest.fixture
def logger(logging_handler: FastAPILoggingHandler) -> Logger:
    test_logger = Logger("test_logger")
    test_logger.addHandler(logging_handler)
    return test_logger


def test_with_logger_message(logging_handler: FastAPILoggingHandler, logger: Logger):
    logger.info("Hello")

    (_, message_payloads), args = logging_handler.transport.send.call_args
    assert args["labels"]["python_logger"] == "test_logger"
    assert args["source_location"] is not None
    assert message_payloads == {"message": "Hello"}


def divide(a, b):
    return a / b


def test_with_logger_exception(logging_handler: FastAPILoggingHandler, logger: Logger):
    try:
        divide(5, 0)
    except ZeroDivisionError as e:
        logger.exception("An error has occurred", exc_info=e)

    (record, message_payloads), args = logging_handler.transport.send.call_args

    assert record.exc_info is None
    assert args["labels"]["python_logger"] == "test_logger"
    assert args["source_location"] is not None
    assert message_payloads["message"] == "An error has occurred"
    assert len(message_payloads["traceback"]) == 2
