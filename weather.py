import asyncio
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("weather")

# Define the API endpoint and parameters
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

async def make_nws_request(url: str) -> dict[str, Any] | None:
  """  Make a request to the NWS API with proper error handling."""
  headers = {
    "User-Agent": USER_AGENT,
    "Accept": "application/geo+json",
  }
  async with httpx.AsyncClient() as client:
    try:
      response = await client.get(url, headers=headers, timeout=30.0)
      response.raise_for_status()
      return response.json()
    except httpx.RequestError as e:
      mcp.logger.error(f"Request error: {e}")
      return None
    except httpx.HTTPStatusError as e:
      mcp.logger.error(f"HTTP error: {e}")
      return None

@mcp.tool()
async def get_alerts(state: str) -> str:
  """Get weather alerts for a specific state.

  Args:
    state (str): The state abbreviation (e.g., 'CA' for California). 
  """
  url = f"{NWS_API_BASE}/alerts/active/area/{state}"
  data = await make_nws_request(url)
  print(data)

  if not data:
    return "Unable to fetch alerts."
  if "features" not in data:
    return "No alerts found."
  if not data["features"]:
    return "No active alerts found."
  
if __name__ == "__main__":
  asyncio.run(get_alerts("CA"))