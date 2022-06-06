from fastapi import APIRouter
from loguru import logger

router = APIRouter()


@router.get("/")
async def root():
    logger.info("Hello")
    return {"message": "Hello World"}


@router.get("/extras")
async def extras():
    logger.info("Hello {user}", user="Bob")
    return {"message": "Hello World with extras"}


@router.get("/error")
async def error():
    logger.error("Hello")
    return {"message": "Something has occurred"}


@router.get("/exception")
async def exception():
    try:
        a = 1
        b = 0
        logger.info(a / b)
    except Exception as error:
        logger.error("Exception. error:{error}", error=error)
    return {"message": "Exception has occurred"}
