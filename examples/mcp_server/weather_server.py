"""
Run this MCP server with:
    python examples/mcp_server/weather_server.py
or:
    python3 examples/mcp_server/weather_server.py
"""

from typing import List
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather")

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather for location."""
    return "It's always sunny in New York"

if __name__ == "__main__":
    mcp.run(transport="sse")