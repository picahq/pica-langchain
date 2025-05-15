"""
Example demonstrating how to use pica-langchain with MCP.
"""

import os
import sys
import asyncio

from langchain_openai import ChatOpenAI
from langchain.agents import AgentType
from pica_langchain import PicaClient, create_pica_agent
from pica_langchain.models import PicaClientOptions

# Configure MCP servers
mcp_options = {
    "math": {
        "command": "python",
        "args": ["./examples/mcp_server/math_server.py"],
        "transport": "stdio",
    },
    "weather": {
        "url": "http://0.0.0.0:8000/sse",
        "transport": "sse",
    }
}

def get_env_var(name: str) -> str:
    """Get environment variable or exit if not set."""
    value = os.environ.get(name)

    if not value:
        print(f"ERROR: {name} environment variable must be set")
        sys.exit(1)

    return value


async def main():
    pica_client = await PicaClient.create(
        secret=get_env_var("PICA_SECRET"),
        options=PicaClientOptions(
            mcp_options=mcp_options,
        ),
    )

    llm = ChatOpenAI(
        temperature=0,
        model="gpt-4o",
    )

    # Create an agent with Pica tools
    agent = create_pica_agent(
        client=pica_client,
        llm=llm,
        agent_type=AgentType.OPENAI_FUNCTIONS,
    )

    import signal

    def handle_sigterm(*args):
        print("\nReceived shutdown signal. Cleaning up...")
        sys.exit(0)
        
    signal.signal(signal.SIGTERM, handle_sigterm)
    signal.signal(signal.SIGINT, handle_sigterm)

    result = await agent.ainvoke(
        {"input": ("First, calculate 25 * 17, then check weather in New York, finally list all connectors Pica supported")}
    )

    print(f"\nWorkflow Result:\n {result}")


if __name__ == "__main__":
    asyncio.run(main())
