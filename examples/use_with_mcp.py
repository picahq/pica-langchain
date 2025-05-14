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

# Set your API keys
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PICA_API_KEY = os.environ.get("PICA_API_KEY")

# Configure MCP servers
mcp_options = {
    "math": {
        "command": "python",
        "args": ["./examples/mcp_server/math_server.py"],
        "transport": "stdio",
    },
    # Uncomment to use a weather server if you have one running
    # "weather": {
    #     "url": "http://localhost:8000/sse",
    #     "transport": "sse",
    # }
}

def get_env_var(name: str) -> str:
    """Get environment variable or exit if not set."""
    value = os.environ.get(name)

    if not value:
        print(f"ERROR: {name} environment variable must be set")
        sys.exit(1)

    return value


async def main():
    try:
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
            system_prompt="Always start your response with `Pica works like ✨\n`",  # Optional: Custom system prompt to append
        )

        result = await agent.ainvoke(
            {"input": ("First, calculate 25 * 17, then check what platforms I have access to.")}
        )

        print(f"\nWorkflow Result:\n {result}")

    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
