"""
Example demonstrating how to use pica-langchain with LangChain in an async context.
This example shows how to properly handle the system prompt in an async environment.
"""

import os
import sys
import asyncio

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


async def main():
    try:
        # Initialize the Pica client
        pica_client = PicaClient(
            secret=get_env_var("PICA_SECRET"),
            options=PicaClientOptions(
                # server_url="https://my-self-hosted-server.com",
                # identity_type="user"
                # identity="user-id",
                authkit=True,                
                # Use ["*"] to initialize all available connections
                connectors=["*"]
            )
        )
        
        # Create an LLM with streaming capability
        llm = ChatOpenAI(
            temperature=0,
            model="gpt-4.1",
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()]
        )

        # Create a Pica agent with the LLM
        # This will now handle the system_prompt correctly in an async context
        agent = create_pica_agent(
            client=pica_client,
            llm=llm,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            return_intermediate_steps=True,
            system_prompt="Always start your response with `Pica works like ✨\n`" # Optional: Custom system prompt to append
        )

        print("\n=== TESTING ASYNC STREAMING WITH SYSTEM PROMPT ===\n")
        
        # Use astream_events for streaming with intermediate steps
        async for chunk in agent.astream_events(
            {"input": "list all available connections"}
        ):
            event_type = chunk.get("event")
            
            # Handle different event types
            if event_type == "on_chat_model_stream":
                # This is a token from the LLM
                content = chunk.get("data", {}).get("chunk", "")
                if content:
                    # We don't print here as the StreamingStdOutCallbackHandler already does it
                    pass
                    
            elif event_type == "on_agent_action":
                # This is an agent action (tool call)
                action = chunk.get("data", {}).get("action", {})
                tool = action.get("tool")
                tool_input = action.get("tool_input", {})
                
                print(f"\n=== AGENT ACTION ===")
                print(f"Tool: {tool}")
                print(f"Input: {tool_input}")
                
            elif event_type == "on_agent_finish":
                # This is the final output
                output = chunk.get("data", {}).get("output")
                print(f"\n=== FINAL OUTPUT ===")
                print(output)
                
        print("\n=== COMPLETED ASYNC TEST ===\n")
        
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
