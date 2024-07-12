from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.api.routes.router import api_router
from app.config.logging_config import log_requests, setup_logging
from app.infra.db.mysql_conector import setup_database

# Setup logging
logger = setup_logging()

# FastAPI configuration
app = FastAPI(
    title="Financial-Api"
)

logger.info("Started application.")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("Setted up CORS Middleware.")

# Include API routes
app.include_router(api_router)
logger.info("Included API routes.")

# Adiciona o middleware globalmente


@app.middleware("http")
async def log_requests_middleware(request, call_next):
    """
    The `log_requests_middleware` function is an asynchronous Python middleware that logs requests
    before passing them to the next handler.

    :param request: The `request` parameter in the `log_requests_middleware` function is typically an
    object that represents the incoming HTTP request. It contains information such as the request
    method, headers, URL, query parameters, and body data. This parameter is used by the middleware to
    inspect and potentially modify the incoming request
    :param call_next: The `call_next` parameter in the `log_requests_middleware` function is a reference
    to the next middleware or endpoint in the chain that should be called after the current middleware.
    When `call_next` is invoked, it will pass the request to the next middleware or endpoint in the
    chain. This
    :return: The `log_requests_middleware` function is returning the result of calling the
    `log_requests` function with the `request` and `call_next` parameters, awaited using the `await`
    keyword.
    """
    return await log_requests(request, call_next)


@app.on_event("startup")
async def startup_event():
    """
    Function `startup_event` initializes database setup.
    """
    setup_database()
    logger.info("Application started successfully.")
