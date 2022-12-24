import pytest
from loguru import logger
from pytest_mock import MockerFixture

from fastapi_cloud_logging.fastapi_cloud_logging_handler import FastAPILoggingHandler


@pytest.fixture
def logging_handler(mocker: MockerFixture) -> FastAPILoggingHandler:
    return FastAPILoggingHandler(
        mocker.Mock(), transport=mocker.Mock(), structured=True
    )


def test_with_logger_message(logging_handler: FastAPILoggingHandler):
    logger.add(logging_handler, format="{message}")
    logger.info("Hello")

    (_, message_payloads), args = logging_handler.transport.send.call_args
    assert args["labels"]["python_logger"] == "tests.test_loguru"
    assert args["source_location"] is not None
    assert message_payloads == {"message": "Hello"}


def divide(a, b):
    return a / b


def test_with_logger_exception(logging_handler: FastAPILoggingHandler):
    logger.add(logging_handler, format="{message}")
    try:
        divide(5, 0)
    except ZeroDivisionError:
        logger.exception("An error has occurred")

    (record, message_payloads), args = logging_handler.transport.send.call_args
    assert record.exc_info is None
    assert args["labels"]["python_logger"] == "tests.test_loguru"
    assert args["source_location"] is not None
    assert message_payloads["message"].startswith("An error has occurred\n")
    assert len(message_payloads["traceback"]) == 2
