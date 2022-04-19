import json

from google.cloud.logging_v2.handlers import CloudLoggingFilter, CloudLoggingHandler
from google.cloud.logging_v2.handlers._helpers import _parse_xcloud_trace
from google.cloud.logging_v2.handlers.handlers import DEFAULT_LOGGER_NAME
from google.cloud.logging_v2.handlers.transports import BackgroundThreadTransport

from .request_logging_middleware import _FASTAPI_REQUEST_CONTEXT


class FastAPILoggingFilter(CloudLoggingFilter):
    """
    This LoggingFilter is extended for logging a request on FastAPI.
    This data can be manually overwritten using the `extras` argument when writing logs.
    """

    def filter(self, record):
        """
        Add new Cloud Logging data to each LogRecord as it comes in
        """
        user_labels = getattr(record, "labels", {})
        # infer request data from context_vars
        (
            inferred_http,
            inferred_trace,
            inferred_span,
            inferred_sampled,
        ) = self.get_request_data()
        if inferred_trace is not None and self.project is not None:
            # add full path for detected trace
            inferred_trace = f"projects/{self.project}/traces/{inferred_trace}"
        # set new record values
        record._resource = getattr(record, "resource", None)
        record._trace = getattr(record, "trace", inferred_trace) or None
        record._span_id = getattr(record, "span_id", inferred_span) or None
        record._trace_sampled = bool(getattr(record, "trace_sampled", inferred_sampled))
        record._http_request = getattr(record, "http_request", inferred_http)
        record._source_location = CloudLoggingFilter._infer_source_location(record)
        # add logger name as a label if possible
        logger_label = {"python_logger": record.name} if record.name else {}
        record._labels = {**logger_label, **self.default_labels, **user_labels} or None
        # create string representations for structured logging
        record._trace_str = record._trace or ""
        record._span_id_str = record._span_id or ""
        record._trace_sampled_str = "true" if record._trace_sampled else "false"
        record._http_request_str = json.dumps(
            record._http_request or {}, ensure_ascii=False
        )
        record._source_location_str = json.dumps(
            record._source_location or {}, ensure_ascii=False
        )
        record._labels_str = json.dumps(record._labels or {}, ensure_ascii=False)
        return True

    def get_request_data(self):
        request = _FASTAPI_REQUEST_CONTEXT.get()
        if request is None:
            return None, None, None, False

        # build up http request data
        http_request = {
            "requestMethod": request.request_method,
            "requestUrl": request.request_url,
            "requestSize": request.content_length,
            "userAgent": request.user_agent,
            "remoteIp": request.remote_ip,
            "referer": request.referer,
            "protocol": request.protocol,
        }

        trace_id, span_id, trace_sampled = _parse_xcloud_trace(
            request.cloud_trace_content
        )
        return http_request, trace_id, span_id, trace_sampled


class FastAPILoggingHandler(CloudLoggingHandler):
    """
    This LoggingHandler is extended for logging a request on FastAPI.
    Usage of this LoggingHandler is the same as CloudLoggingHandler.
    """

    def __init__(
        self,
        client,
        *,
        name=DEFAULT_LOGGER_NAME,
        transport=BackgroundThreadTransport,
        resource=None,
        labels=None,
        stream=None,
    ):
        """
        Args:
            client (~logging_v2.client.Client):
                The authenticated Google Cloud Logging client for this
                handler to use.
            name (str): the name of the custom log in Cloud Logging.
                Defaults to 'python'. The name of the Python logger will be represented
                in the ``python_logger`` field.
            transport (~logging_v2.transports.Transport):
                Class for creating new transport objects. It should
                extend from the base :class:`.Transport` type and
                implement :meth`.Transport.send`. Defaults to
                :class:`.BackgroundThreadTransport`. The other
                option is :class:`.SyncTransport`.
            resource (~logging_v2.resource.Resource):
                Resource for this Handler. If not given, will be inferred from the environment.
            labels (Optional[dict]): Additional labels to attach to logs.
            stream (Optional[IO]): Stream to be used by the handler.
        """
        super(FastAPILoggingHandler, self).__init__(
            client,
            name=name,
            transport=transport,
            resource=resource,
            labels=labels,
            stream=stream,
        )

        # replace default cloud logging filter
        for default_filter in self.filters:
            if isinstance(default_filter, CloudLoggingFilter):
                self.removeFilter(default_filter)

        log_filter = FastAPILoggingFilter(
            project=self.project_id, default_labels=labels
        )
        self.addFilter(log_filter)
