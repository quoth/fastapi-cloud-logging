from fastapi import FastAPI
from google.cloud.logging import Client
from google.cloud.logging_v2.handlers import setup_logging

from fastapi_cloud_logging import FastAPILoggingHandler, RequestLoggingMiddleware

from .root import router as root_router

app = FastAPI()
app.add_middleware(RequestLoggingMiddleware)

handler = FastAPILoggingHandler(Client())
setup_logging(handler)

app.include_router(root_router, prefix="", tags=["base"])
