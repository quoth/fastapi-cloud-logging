from contextvars import ContextVar
from dataclasses import dataclass
from typing import Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


@dataclass
class FastAPIRequestContext:
    request_method: str
    """HTTP Method Name"""
    request_url: str
    """HTTP Request URI"""
    content_length: Optional[int]
    """Size of the message body"""
    user_agent: str
    """User Agent"""
    remote_ip: Optional[str]
    """Remote IP Address"""
    referer: Optional[str]
    """HTTP Referer"""
    protocol: str
    """HTTP Protocol Scheme"""
    cloud_trace_content: Optional[str]
    """Cloud Trace Header"""


_FASTAPI_REQUEST_CONTEXT: ContextVar[Optional[FastAPIRequestContext]] = ContextVar(
    "fastapi_request_context", default=None
)
_HTTP_CONTENT_LENGTH = "content-length"
_HTTP_USER_AGENT = "user-agent"
_HTTP_FORWARDED_FOR_HEADER = "x-forwarded-for"
_HTTP_REFERER_HEADER = "referer"
_HTTP_TRACE_HEADER = "x-cloud-trace-context"


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        self.set_request_context(request=request)
        return await call_next(request)

    def set_request_context(self, request: Request) -> None:
        _FASTAPI_REQUEST_CONTEXT.set(self._parse_request(request))

    def _parse_request(self, request: Request) -> FastAPIRequestContext:
        return FastAPIRequestContext(
            request_method=request.method,
            request_url=str(request.url),
            content_length=self._parse_content_length(
                request.headers.get(_HTTP_CONTENT_LENGTH)
            ),
            user_agent=request.headers.get(_HTTP_USER_AGENT),
            remote_ip=request.headers.get(
                _HTTP_FORWARDED_FOR_HEADER, request.client.host
            ),
            referer=request.headers.get(_HTTP_REFERER_HEADER),
            protocol=request.url.scheme,
            cloud_trace_content=request.headers.get(_HTTP_TRACE_HEADER),
        )

    def _parse_content_length(self, content_header: Optional[str]) -> Optional[int]:
        if content_header is None:
            return None
        content_length = None
        try:
            content_length = int(content_header)
        except (ValueError, TypeError):
            content_length = None
        return content_length
