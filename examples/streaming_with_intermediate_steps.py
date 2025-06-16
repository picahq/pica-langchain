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
            model="gpt-4.1",
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()]
        )

        agent_with_handler = create_pica_agent(
            client=pica_client,
            llm=llm_with_handler,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            return_intermediate_steps=True
        )

        for chunk in agent_with_handler.stream({
            "input": "What actions can I perform on google calendar?"
        }):
            # Check for intermediate_steps in the chunk
            if "intermediate_steps" in chunk:
                print("\n=== INTERMEDIATE STEPS ===")
                for step in chunk["intermediate_steps"]:
                    # Handle different possible formats of the step
                    action = step[0]
                    output = step[1]
                    
                    # Print action info with proper attribute access
                    print(f"Tool: {action.tool if hasattr(action, 'tool') else 'Unknown'}")
                    
                    # Get the tool input (different ways it might be structured)
                    if hasattr(action, 'tool_input'):
                        tool_input = action.tool_input
                    elif hasattr(action, 'args'):
                        tool_input = action.args
                    else:
                        tool_input = str(action)
                        
                    print(f"Input: {tool_input}")
                    print(f"Output: {output}")
                    print("---")
        
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 