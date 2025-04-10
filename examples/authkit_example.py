"""
Example demonstrating how to use pica-langchain with LangChain.
"""

import os
import sys

from langchain_openai import ChatOpenAI
from langchain.agents import AgentType
from pica_langchain import PicaClient, create_pica_agent
from pica_langchain.models import PicaClientOptions


def get_env_var(name: str) -> str:
    """Get environment variable or exit if not set."""
    value = os.environ.get(name)

    if not value:
        print(f"ERROR: {name} environment variable must be set")
        sys.exit(1)

    return value


def main():
    try:
        pica_client = PicaClient(
            secret=get_env_var("PICA_SECRET"),
            options=PicaClientOptions(
                authkit=True, # Enable AuthKit settings
                connectors=["*"]
            )
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
            return_intermediate_steps=True # Show the intermediate steps
        )

        result = agent.invoke({
            "input": (
                "Connect to Google Calendar" # This will trigger the promptToConnectPlatform tool if the user doesn't have google calendar connected
            )
        })
        
        print(f"\nWorkflow Result:\n {result}")
    
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
