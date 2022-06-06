import pytest
from fastapi import Request
from pytest_mock import MockerFixture
from starlette.datastructures import Headers

from fastapi_cloud_logging.request_logging_middleware import (
    _FASTAPI_REQUEST_CONTEXT,
    RequestLoggingMiddleware,
)


@pytest.fixture
def middleware(mocker: MockerFixture) -> RequestLoggingMiddleware:
    return RequestLoggingMiddleware(app=mocker.Mock(), dispatch=mocker.Mock())


def test__set_request_context(middleware: RequestLoggingMiddleware):
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "root_path": "https://example.com/",
            "path": "",
            "headers": Headers({}).raw,
            "client": ("127.0.0.1", 80),
        }
    )
    middleware.set_request_context(request=request)
    request_context = _FASTAPI_REQUEST_CONTEXT.get()
    assert request_context is not None
    assert request_context.protocol == "https"
    assert request_context.request_method == "GET"


@pytest.mark.parametrize(
    (
        "example_request, http_method, protocol, ip_address, content_length,"
        "url, user_agent, referer, trace_content"
    ),
    [
        (
            Request(
                {
                    "type": "http",
                    "method": "GET",
                    "root_path": "https://example.com/",
                    "path": "",
                    "headers": Headers({"X-Forwarded-For": "192.168.0.1"}).raw,
                    "client": ("127.0.0.1", 80),
                }
            ),
            "GET",
            "https",
            "192.168.0.1",
            None,
            "https://example.com/",
            None,
            None,
            None,
        ),
        (
            Request(
                {
                    "type": "http",
                    "method": "POST",
                    "root_path": "https://example.com/",
                    "path": "",
                    "headers": Headers(
                        {"User-Agent": "curl 7.79.1", "X-Forwarded-For": "192.168.0.1"}
                    ).raw,
                    "client": ("127.0.0.1", 80),
                }
            ),
            "POST",
            "https",
            "192.168.0.1",
            None,
            "https://example.com/",
            "curl 7.79.1",
            None,
            None,
        ),
        (
            Request(
                {
                    "type": "http",
                    "method": "POST",
                    "root_path": "https://example.com/",
                    "path": "",
                    "headers": Headers(
                        {
                            "User-Agent": "curl 7.79.1",
                            "X-Forwarded-For": "192.168.0.1",
                            "X-Cloud-Trace-Context": "105445aa7843bc8bf206b12000100000/1;o=1",
                        }
                    ).raw,
                    "client": ("127.0.0.1", 80),
                }
            ),
            "POST",
            "https",
            "192.168.0.1",
            None,
            "https://example.com/",
            "curl 7.79.1",
            None,
            "105445aa7843bc8bf206b12000100000/1;o=1",
        ),
    ],
)
def test__parse_request(
    middleware: RequestLoggingMiddleware,
    example_request: Request,
    http_method,
    protocol,
    ip_address,
    content_length,
    url,
    user_agent,
    referer,
    trace_content,
):
    request_context = middleware._parse_request(example_request)
    assert request_context.request_method == http_method
    assert request_context.protocol == protocol
    assert request_context.content_length == content_length
    assert request_context.request_url == url
    assert request_context.remote_ip == ip_address
    assert request_context.user_agent == user_agent
    assert request_context.referer == referer
    assert request_context.cloud_trace_content == trace_content
