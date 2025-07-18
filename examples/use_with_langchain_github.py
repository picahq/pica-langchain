"""
Example demonstrating how to use pica-langchain with LangChain 
to execute a multi-step workflow using the GitHub Connector.
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
                connectors=["your-github-connector-key"] # Replace with your GitHub connector key
            )
        )

        pica_client.initialize()
        
        llm = ChatOpenAI(
            temperature=0,
            model="gpt-4.1",
        )

        # Create an agent with Pica tools
        agent = create_pica_agent(
            client=pica_client,
            llm=llm,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            # return_intermediate_steps=True, # Optional: Return intermediate steps
        )

        # Execute a multi-step workflow using the GitHub Connector
        result = agent.invoke({
            "input": (
                "Star the picahq/pica repo in github. "
                "Then, list 5 of the repositories that I have starred in github."
            )
        })
        
        print(f"\nGitHub Agent Result:\n {result}")
    
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
