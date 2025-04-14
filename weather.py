from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

# Initialize FastMCP server
mcp = FastMCP("weather", log_level="ERROR")

# Define the API endpoint and parameters
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"


async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json",
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError:
            return None
        except httpx.HTTPStatusError:
            return None


def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Event: {props.get("event", "Unknown")}
Area: {props.get("areaDesc", "Unknown")}
Severity: {props.get("severity", "Unknown")}
Description: {props.get("description", "No description available")}
Instructions: {props.get("instruction", "No specific instructions provided")}
"""


@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a specific state.

    Args:
        state (str): The state abbreviation (e.g., 'CA' for California).
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data:
        return "Unable to fetch alerts."
    if "features" not in data:
        return "No alerts found."
    if not data["features"]:
        return "No active alerts found."
    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "Unable to fetch forecast data for this location."

    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "Unable to fetch detailed forecast."

    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # Only show next 5 periods
        forecast = f"""
{period["name"]}:
Temperature: {period["temperature"]}°{period["temperatureUnit"]}
Wind: {period["windSpeed"]} {period["windDirection"]}
Forecast: {period["detailedForecast"]}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)

@mcp.prompt()
def review_code(code: str) -> str:
    """
    Generates a review prompt for the given code.

    Args:
        code (str): The code snippet to be reviewed.

    Returns:
        str: A formatted string prompting for a review of the provided code.
    """
    return "Please review the following code:\n" + code + "\n\n### Review:\n"


# Q. User message와 Assistant message의 차이점은?
# A. User message는 사용자가 입력하는 메시지이고, Assistant message는 AI가 응답하는 메시지입니다.
# Ref: https://platform.openai.com/docs/guides/prompt-engineering
# No DeveloperMessage(!)
# Usage of assistant message: To generate a response from example, you can use the AssistantMessage class to create a message that represents the AI's response.
# #x) (Tactic: Provide examples in ref)
@mcp.prompt()
def debug_error(error: str) -> list[base.Message]:
    """
    Generates a list of messages to assist in debugging an error.

    Args:
        error (str): The error message to be debugged.

    Returns:
        list[base.Message]: A list of messages including a prompt for debugging assistance.
    """
    return [
        base.UserMessage("You are a helpful assistant that helps debug errors."),
        base.UserMessage(f"Please help me debug the following error:\n{error}"),
        base.AssistantMessage(
            "Sure! Please provide the error message and any relevant code snippets."
        ),
    ]

if __name__ == "__main__":
    mcp.run(transport="stdio")
