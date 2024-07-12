from fastapi import HTTPException, Request
from fastapi.responses import StreamingResponse
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import time
from typing import Optional, TextIO


class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    stream: Optional[TextIO] = None

    def __init__(self, filename, when='h', interval=1, backupCount=0,
                 encoding=None, delay=False, utc=False, atTime=None):
        super().__init__(filename, when, interval, backupCount, encoding, delay, utc, atTime)

    def doRollover(self):
        """
        Do a rollover; in this case, a date/time stamp is appended to the filename
        when the rollover happens. However, you want the filename to be in the format
        'app.YYYY-MM-DD.log'.
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple
        currentTime = int(time.time())
        t = self.rolloverAt - self.interval
        timeTuple = time.localtime(t)

        # Customizing the rollover filename
        dfn = f"{self.baseFilename}.{time.strftime('%Y-%m-%d', timeTuple)}.log"

        if os.path.exists(dfn):
            os.remove(dfn)

        self.rotate(self.baseFilename, dfn)

        if not self.delay:
            self.stream = self._open()

        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt += self.interval

        if self.utc:
            timeTuple = time.gmtime(newRolloverAt)
        else:
            timeTuple = time.localtime(newRolloverAt)

        self.rolloverAt = int(time.mktime(timeTuple))


def setup_logging():
    """
    The `setup_logging` function configures logging for an application, including writing logs to a file
    and displaying colored log messages in the console.
    :return: The `setup_logging()` function returns a configured logger object that has handlers for
    writing logs to a file and to the console with colored level names.
    """
    # Main logger configuration
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Check if handlers are already added to avoid duplication
    if not logger.handlers:
        # Handler for info logs to file
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s")
        handler = CustomTimedRotatingFileHandler(
            "app.log", when="midnight", backupCount=7)
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Console handler for info logs with colored levelname
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        class ColoredFormatter(logging.Formatter):
            COLORS = {
                'INFO': '\033[94mAPP',
                'ERROR': '\033[91mAPP',
                'DEBUG': '\033[95mAPP'
            }
            RESET = {
                'INFO': '\033[0m ',
                'ERROR': '\033[0m',
                'DEBUG': '\033[0m'
            }

            def format(self, record):
                levelname = record.levelname
                if levelname in self.COLORS:
                    record.levelname = f"{self.COLORS[levelname]}{levelname}:{self.RESET[levelname]}"
                return super().format(record)

        console_formatter = ColoredFormatter('%(levelname)s %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger


logger = setup_logging()


async def log_requests(request: Request, call_next):
    """
    Middleware para logar informações sobre as requisições HTTP.
    """

    try:
        logger.info(f"Received request: {request.method} {request.url}")
        logger.info(f"Request headers: {request.headers}")
        logger.info(f"Request body: {await request.body()}")
        logger.info(f"Request query parameters: {request.query_params}")

        response = await call_next(request)

        logger.info(f"Responded with: {response.status_code}")
        logger.info(f"Response headers: {response.headers}")

        if isinstance(response, StreamingResponse):
            logger.info(f"Response is a StreamingResponse, capturing body...")
            response_body = bytearray()
            async for chunk in response.body_iterator:
                if isinstance(chunk, bytes):
                    response_body.extend(chunk)
                elif isinstance(chunk, str):
                    response_body.extend(chunk.encode())
                else:
                    logger.warning(f"Ignoring chunk of type {type(chunk)}")
            logger.info(f"Response body: {response_body.decode('utf-8')}")
            response = StreamingResponse(
                iter([bytes(response_body)]),
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
        else:
            if isinstance(response.body, bytes):
                logger.info(f"Response body: {response.body.decode('utf-8')}")
            else:
                logger.info(f"Response body: {response.body}")
            logger.info(f"Response content: {response.content}")
            logger.info(f"Response media type: {response.media_type}")

        return response

    except HTTPException as http_exc:
        logger.error(f"HTTPException: {http_exc}")
        raise http_exc

    except Exception as exc:
        logger.error(f"Exception occurred: {exc}")
        raise exc
