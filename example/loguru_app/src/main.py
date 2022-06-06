import logging

from fastapi import FastAPI
from google.cloud.logging import Client
from loguru import logger

from fastapi_cloud_logging import FastAPILoggingHandler, RequestLoggingMiddleware

from .root import router as root_router

app = FastAPI()
app.add_middleware(RequestLoggingMiddleware)

try:
    handler = FastAPILoggingHandler(Client(), structured=True)
    config = {
        "handlers": [
            {"sink": handler, "level": logging.INFO, "format": "{time} - {message}"},
        ],
    }
    logger.remove()
    logger.configure(**config)
except Exception:
    import sys

    config = {
        "handlers": [
            {"sink": sys.stdout, "format": "{time} - {message}"},
        ],
    }
    logger.configure(**config)

app.include_router(root_router, prefix="", tags=["base"])
