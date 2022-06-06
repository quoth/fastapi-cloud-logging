from logging import LogRecord

import pytest
from pytest_mock import MockerFixture

from fastapi_cloud_logging.fastapi_cloud_logging_handler import (
    FastAPILoggingFilter,
    FastAPILoggingHandler,
)
from fastapi_cloud_logging.request_logging_middleware import (
    _FASTAPI_REQUEST_CONTEXT,
    FastAPIRequestContext,
)


@pytest.fixture
def logging_filter(mocker: MockerFixture) -> FastAPILoggingFilter:
    return FastAPILoggingFilter()


@pytest.fixture
def structured_logging_filter(mocker: MockerFixture) -> FastAPILoggingFilter:
    return FastAPILoggingFilter(structured=True)


@pytest.fixture
def logging_handler(mocker: MockerFixture) -> FastAPILoggingHandler:
    return FastAPILoggingHandler(mocker.Mock(), transport=mocker.Mock())


def test_filter_without_request(logging_filter: FastAPILoggingFilter):
    log_record: LogRecord = LogRecord(
        name="some_log",
        level=3,
        pathname="tests/test_fastapi_cloud_logging_handler.py",
        lineno=31,
        msg="info",
        args=None,
        exc_info=None,
    )
    filtered = logging_filter.filter(log_record)
    assert filtered is True
    assert log_record._trace is None
    assert log_record._span_id is None
    assert log_record._trace_sampled is False
    assert log_record._http_request is None


def test_filter_with_loguru_extra(logging_filter: FastAPILoggingFilter):
    log_record: LogRecord = LogRecord(
        name="some_log",
        level=3,
        pathname="tests/test_fastapi_cloud_logging_handler.py",
        lineno=31,
        msg="info",
        args=None,
        exc_info=None,
    )
    setattr(log_record, "extra", {"user_id": "user1234"})
    filtered = logging_filter.filter(log_record)
    assert filtered is True
    assert log_record._trace is None
    assert log_record._span_id is None
    assert log_record._trace_sampled is False
    assert log_record._http_request is None
    assert log_record.json_fields["user_id"] == "user1234"


def test_filter_with_request(logging_filter: FastAPILoggingFilter):
    _FASTAPI_REQUEST_CONTEXT.set(
        FastAPIRequestContext(
            request_method="GET",
            request_url="https://example.com/api/v1/users/me",
            content_length=None,
            user_agent="curl/7.77.0",
            remote_ip="127.0.0.1",
            referer=None,
            protocol="https",
            cloud_trace_content="105445ab7f43bc8bf206b12000100000/2a;o=1",
        )
    )
    log_record: LogRecord = LogRecord(
        name="some_log",
        level=3,
        pathname="tests/test_fastapi_cloud_logging_handler.py",
        lineno=31,
        msg="info",
        args=None,
        exc_info=None,
    )
    filtered = logging_filter.filter(log_record)
    assert filtered is True
    assert log_record._trace == "105445ab7f43bc8bf206b12000100000"
    assert log_record._span_id == "2a"
    assert log_record._trace_sampled is True
    assert log_record._http_request == {
        "requestMethod": "GET",
        "requestUrl": "https://example.com/api/v1/users/me",
        "requestSize": None,
        "userAgent": "curl/7.77.0",
        "remoteIp": "127.0.0.1",
        "referer": None,
        "protocol": "https",
    }
    assert log_record.msg == "info"


def test_structured_filter(structured_logging_filter: FastAPILoggingFilter):
    _FASTAPI_REQUEST_CONTEXT.set(None)
    log_record: LogRecord = LogRecord(
        name="some_log",
        level=3,
        pathname="tests/test_fastapi_cloud_logging_handler.py",
        lineno=31,
        msg="info",
        args=None,
        exc_info=None,
    )
    filtered = structured_logging_filter.filter(log_record)
    assert filtered is True
    assert log_record._http_request is None
    assert log_record.msg == {"message": "info"}


@pytest.mark.parametrize("sample_request_method", ["GET", None])
@pytest.mark.parametrize(
    "sample_request_url", ["https://example.com/api/v1/users/me", None]
)
@pytest.mark.parametrize("sample_content_length", [64, 0, None])
@pytest.mark.parametrize("sample_user_agent", ["curl/7.77.0", None])
@pytest.mark.parametrize("sample_remote_ip", ["127.0.0.1", None])
@pytest.mark.parametrize("sample_referer", ["https://example.com/api/v1/signin", None])
@pytest.mark.parametrize("sample_protocol", ["https", None])
@pytest.mark.parametrize(
    "sample_cloud_trace_content", ["105445aa7843bc8bf206b12000100000/2a;o=1", None]
)
def test_get_request_data(
    logging_filter: FastAPILoggingFilter,
    sample_request_method,
    sample_request_url,
    sample_content_length,
    sample_user_agent,
    sample_remote_ip,
    sample_protocol,
    sample_referer,
    sample_cloud_trace_content,
):
    _FASTAPI_REQUEST_CONTEXT.set(
        FastAPIRequestContext(
            request_method=sample_request_method,
            request_url=sample_request_url,
            content_length=sample_content_length,
            user_agent=sample_user_agent,
            remote_ip=sample_remote_ip,
            referer=sample_referer,
            protocol=sample_protocol,
            cloud_trace_content=sample_cloud_trace_content,
        )
    )
    request, trace_id, span_id, trace_sampled = logging_filter.get_request_data()
    assert request is not None
    assert request["requestMethod"] == sample_request_method
    assert request["requestUrl"] == sample_request_url
    assert request["requestSize"] == sample_content_length
    assert request["userAgent"] == sample_user_agent
    assert request["remoteIp"] == sample_remote_ip
    assert request["protocol"] == sample_protocol
    assert request["referer"] == sample_referer
    if sample_cloud_trace_content is not None:
        assert trace_id == "105445aa7843bc8bf206b12000100000"
        assert span_id == "2a"
        assert trace_sampled is True
    else:
        assert trace_id is None
        assert span_id is None
        assert trace_sampled is False


def test_get_request_data_with_no_context(logging_filter: FastAPILoggingFilter):
    _FASTAPI_REQUEST_CONTEXT.set(None)
    request, trace_id, span_id, trace_sampled = logging_filter.get_request_data()
    assert request is None
    assert trace_id is None
    assert span_id is None
    assert trace_sampled is False
