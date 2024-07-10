from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from app.api.main import api_router
from dotenv import load_dotenv

def custom_generate_unique_id(route: APIRoute) -> str:
    """
    The function `custom_generate_unique_id` generates a unique ID by combining the first tag and name
    of an API route.
    
    :param route: The `route` parameter is an object representing an API route. It likely contains
    information such as the route's tags and name
    :type route: APIRoute
    :return: The function `custom_generate_unique_id` returns a string that combines the first tag of
    the API route and the name of the route separated by a hyphen.
    """
    return f"{route.tags[0]}-{route.name}"



load_dotenv()


app = FastAPI(
    title="Finantial-Api",
    generate_unique_id_function=custom_generate_unique_id
)

app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "*"
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router)