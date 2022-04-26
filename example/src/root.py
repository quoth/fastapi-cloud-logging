import logging

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root():
    logging.info("Hello")
    return {"message": "Hello World"}


@router.get("/extras")
async def extras():
    logging.info("Hello", extra={"json_fields": {"user": "Bob"}})
    return {"message": "Hello World with extras"}


@router.get("/error")
async def error():
    logging.error("Hello")
    return {"message": "Something has occurred"}
