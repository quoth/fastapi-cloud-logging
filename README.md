# fastapi-cloud-logging

[![Test](https://github.com/quoth/fastapi-cloud-logging/actions/workflows/test.yaml/badge.svg)](https://github.com/quoth/fastapi-cloud-logging/actions/workflows/test.yaml)

## Project description

fastapi-cloud-logging improves cloud logging with fastapi. It enables to send request data on cloud logging.

## Dependencies

* fastapi
* cloud logging
* Python >= 3.7
  * Require [contextvars](https://docs.python.org/3/library/contextvars.html)

## Installation

```sh
pip install fastapi-cloud-logging
```

## Usage

Add a middleware and set a handler to send a request info with each logging.

```python
from fastapi import FastAPI
from google.cloud.logging import Client
from google.cloud.logging_v2.handlers import setup_logging

from fastapi_cloud_logging import FastAPILoggingHandler, RequestLoggingMiddleware

app = FastAPI()

# Add middleware
app.add_middleware(RequestLoggingMiddleware)

# Use manual handler
handler = FastAPILoggingHandler(Client())
setup_logging(handler)
```

## Optional

### Structured Message

Cloud logging supports log entries with structured and unstructured data.
When a log record has a structured data, it write a log entry with structured data. And when a log record contains a string message, it write a log entry as an unstructured textPayload attribute.

When this structured option set True on FastAPILoggingHandler, it always write a log entry with a message attribute on a structured jsonPayload object.

```python
# default structured value is False
handler = FastAPILoggingHandler(Client(), structured=True)
```

## Changelog

[`CHANGELOG.md`](CHANGELOG.md)

## Appendix

### With multithreading

This middleware depends mainly contextvars. So, when you use multithreading, it cannot handle a request info. On this case, you write a code for manual context management. For example, use `copy_context` on a thread.

For more information, please read [a great article about contextvars][1].

[1]: https://kobybass.medium.com/python-contextvars-and-multithreading-faa33dbe953d
