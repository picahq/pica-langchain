"""
Example demonstrating how to use pica-langchain with LangChain streaming responses.
"""

import os
import sys

from langchain_openai import ChatOpenAI
from langchain.agents import AgentType
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
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
                connectors=["*"], # Initialize all available connections for this example
            )
        )
        
        llm_with_handler = ChatOpenAI(
            temperature=0,
            model="gpt-4o",
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()]
        )

        agent_with_handler = create_pica_agent(
            client=pica_client,
            llm=llm_with_handler,
            agent_type=AgentType.OPENAI_FUNCTIONS,
        )

        for chunk in agent_with_handler.stream({
            "input": "List three platforms available in Pica."
        }):
            print(chunk)
        
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 