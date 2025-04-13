from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp.server.fastmcp import FastMCP


# dataclass는 type annotation이 있는 field를 기반으로 __init__, __eq__, __repr__, __hash__ 등을 자동으로 생성해주는 decorator
@dataclass
class AppContext:
    """
    AppContext serves as a container for application-wide dependencies.

    Attributes:
        db (Database): An instance of the Database class used for managing
        database operations within the application.
    """

    db: Database


# context manager manages runtime context, declres __aenter__ and __aexit__ methods
# the function being decorated must return a generator when called. This generator must yield exactly one value.
# when next(iterator) is called, the function will run until it hits the yield statement, at which point it will return the value yielded.
# the function will then pause until the next call to next(iterator) or iterator is closed.
@asynccontextmanager
async def app_lifespan(_: FastMCP) -> AsyncIterator[AppContext]:
    """Lifespan context manager for the FastMCP server."""
    try:
        # Initialize resources
        db = Database()
        # Yield the context
        yield AppContext(db=db)
    finally:
        # Cleanup resources
        await db.close()


# lifespan = runtime context: You can use it to initialize/cleanup resources when the server starts/stops
# also, lifespan can be used to pass data to request handlers via lifespan API
mcp = FastMCP("swiftmr", log_level="ERROR", lifespan=app_lifespan)


@mcp.resource("config://app")
def get_config() -> str:
    """
    Retrieve the application configuration data.

    Returns:
        str: A string containing the application configuration data.
    """
    return "App config data"

@mcp.resource("users://{user_id}/profile")
def get_user_profile(user_id: str) -> str:
    """
    Retrieve the user profile data for the specified user ID.

    Args:
        user_id (str): The ID of the user whose profile data is to be retrieved.

    Returns:
        str: A string containing the user profile data.
    """
    return f"User {user_id} profile data"

@mcp.tool()
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Calculate BMI given weight in kg and height in meters"""
    return weight_kg / (height_m**2)


@mcp.tool()
async def fetch_weather(city: str) -> str:
    """Fetch current weather for a city"""
    async with httpx.AsyncClient() as client:  # noqa: F821
        response = await client.get(f"https://api.weather.com/{city}")
        return response.text