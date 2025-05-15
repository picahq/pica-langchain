# test_mcp_server.py
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.callbacks.manager import CallbackManagerForToolRun


async def test_server():
    server_params = StdioServerParameters(
        command="python",
        args=["./examples/mcp_server/math_server.py"],
    )

    print("Connecting to server...")
    async with stdio_client(server_params) as (read, write):
        print("Connected to server, initializing session...")
        async with ClientSession(read, write) as session:
            print("Session initialized, initializing connection...")
            await session.initialize()
            print("Connection initialized, loading tools...")
            tools = await load_mcp_tools(session)
            print(f"Loaded {len(tools)} tools:")

            for tool in tools:
                print(f"- {tool.name}: {tool.description}")


if __name__ == "__main__":
    asyncio.run(test_server())
