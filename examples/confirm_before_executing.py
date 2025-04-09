"""
Example demonstrating how to use pica-langchain with LangChain 
to execute a multi-step workflow using the GitHub Connector, with
a custom confirmation callback that prevents duplicate execution.
"""

import os
import sys

from langchain_openai import ChatOpenAI
from langchain.agents import AgentType
from pica_langchain import PicaClient, create_pica_agent, ExecuteTool
from pica_langchain.models import PicaClientOptions
from langchain.callbacks.base import BaseCallbackHandler

# Custom exception for halting normal tool execution after confirmation.
class ToolExecutionComplete(Exception):
    def __init__(self, result):
        self.result = result


def get_env_var(name: str) -> str:
    """Get environment variable or exit if not set."""
    value = os.environ.get(name)
    if not value:
        print(f"ERROR: {name} environment variable must be set")
        sys.exit(1)
    return value


class CustomCallbackHandler(BaseCallbackHandler):
    def __init__(self, pica_client):
        self.pica_client = pica_client

    def on_agent_action(self, action, **kwargs):
        # Intercept only for the "execute" tool.
        if action.tool == "execute":
            print("\n\n⚠️  INTERCEPTING TOOL EXECUTION FOR CONFIRMATION  ⚠️\n\n")

            execute_tool_input = action.tool_input
            message_log = action.message_log

            print("Do you want to execute this tool?")
            # Show a summary of what it is going to do.
            for message in message_log:
                if hasattr(message, "content") and message.content:
                    print("\nConfirmation of email to send:")
                    print("-" * 40)
                    print(message.content)
                    print("-" * 40)

            user_input = input("Enter 'y' to execute, 'n' to skip: ")

            if user_input.lower() == "y":
                execute_tool = ExecuteTool(client=self.pica_client)
                # Call the execution method with the intercepted parameters.
                try:
                    result = execute_tool._run(
                        platform=execute_tool_input.get("platform"),
                        action_id=execute_tool_input.get("action_id"),
                        action_path=execute_tool_input.get("action_path"),
                        method=execute_tool_input.get("method"),
                        connection_key=execute_tool_input.get("connection_key"),
                        data=execute_tool_input.get("data"),
                        path_variables=execute_tool_input.get("path_variables"),
                        query_params=execute_tool_input.get("query_params"),
                        headers=execute_tool_input.get("headers"),
                        is_form_data=execute_tool_input.get("is_form_data", False),
                        is_url_encoded=execute_tool_input.get("is_url_encoded", False),
                    )
                    # Instead of returning the result normally,
                    # raise a custom exception carrying the result. This
                    # stops the agent's normal execution flow.
                    raise ToolExecutionComplete(result)
                except Exception as e:
                    print(e)
                    sys.exit(1)
            else:
                print("Skipping tool execution.")
                sys.exit(1)


def main():
    try:
        pica_client = PicaClient(
            secret=get_env_var("PICA_SECRET"),
            options=PicaClientOptions(
                connectors=["*"]  # Replace with your GitHub connector key if needed.
            ),
        )

        callback_handler = CustomCallbackHandler(pica_client)

        llm = ChatOpenAI(
            temperature=0,
            model="gpt-4o",
        )

        agent = create_pica_agent(
            client=pica_client,
            llm=llm,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            callbacks=[callback_handler],
        )

        # Wrap agent invocation to catch our short-circuit exception.
        try:
            result = agent.invoke({
                "input": "Send an email to paul@picaos.com with a funny joke using gmail"
            })
            print(f"\nPica Agent Result:\n{result}")
        except ToolExecutionComplete as tec:
            # Use the result carried by our custom exception.
            print(f"\nPica Agent Result (via confirmed execution):\n{tec.result}")

    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
