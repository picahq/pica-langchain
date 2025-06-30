"""
Example demonstrating how to use pica-langchain with LangChain's streaming API (astream_events)
to execute a multi-step workflow with confirmation before executing.
"""

import os
import sys
import asyncio
import json
from typing import Any, Dict, Optional
import functools

from langchain_openai import ChatOpenAI
from langchain.agents import AgentType
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema.agent import AgentAction
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from pica_langchain import PicaClient, create_pica_agent, ExecuteTool
from pica_langchain.models import PicaClientOptions


def get_env_var(name: str) -> str:
    """Get environment variable or exit if not set."""
    value = os.environ.get(name)
    if not value:
        print(f"ERROR: {name} environment variable must be set")
        sys.exit(1)
    return value


# Function to wrap ExecuteTool._run method with confirmation
def with_confirmation(func):
    """Decorator to add confirmation to ExecuteTool._run method."""
    @functools.wraps(func)
    def wrapper(self, 
                platform: str,
                action_id: str,
                action_path: str,
                method: str,
                connection_key: str,
                data: Optional[Dict[str, Any]] = None,
                path_variables: Optional[Dict[str, Any]] = None,
                query_params: Optional[Dict[str, Any]] = None,
                headers: Optional[Dict[str, Any]] = None,
                is_form_data: bool = False,
                is_url_encoded: bool = False,
                run_manager = None):
        """Wrapped version of ExecuteTool._run that adds confirmation."""
        print("\n\n⚠️  INTERCEPTING TOOL EXECUTION FOR CONFIRMATION  ⚠️\n\n")
        
        tool_input = {
            "platform": platform,
            "action_id": action_id,
            "action_path": action_path,
            "method": method,
            "connection_key": connection_key,
            "data": data or {},
            "path_variables": path_variables or {},
            "query_params": query_params or {},
            "headers": headers or {}
        }
        print(f"Tool input: {json.dumps(tool_input, indent=2)}")
        
        user_input = input("\nEnter 'y' to execute, 'n' to skip: ")
        
        if user_input.lower() == "y":
            return func(self, 
                platform=platform,
                action_id=action_id,
                action_path=action_path,
                method=method,
                connection_key=connection_key,
                data=data,
                path_variables=path_variables,
                query_params=query_params,
                headers=headers,
                is_form_data=is_form_data,
                is_url_encoded=is_url_encoded,
                run_manager=run_manager
            )
        else:
            print("Tool execution skipped by user")
            
            mock_response = {
                "success": True,
                "message": "Tool execution skipped by user",
                "action": action_id,
                "platform": platform
            }

            return json.dumps(mock_response)
            
    return wrapper


class StreamingConfirmationHandler(BaseCallbackHandler):
    """Callback handler for streaming output."""
    
    def __init__(self):
        pass
    

async def stream_and_process(agent, query: str):
    """Stream agent output while handling tool confirmations."""
    print("\n🤖 Agent is processing your request with streaming...\n")
    print("AI: ", end="", flush=True)
    
    async for event in agent.astream_events({"input": query}):
        event_type = event.get("event")
        
        if event_type == "on_chat_model_stream":
            chunk = event.get("chunk")
            if chunk and hasattr(chunk, "content") and chunk.content:
                print(chunk.content, end="", flush=True)
            
        elif event_type == "on_tool_end":
            result = event.get("output")

            if isinstance(result, dict):
                formatted_result = json.dumps(result, indent=2)
            else:
                formatted_result = str(result)
                
            print(f"\n[Tool result: {formatted_result}]")
            print("\nAI: ", end="", flush=True)
    
    print("\n\n✅ Request completed")

async def main():
    try:
        original_run = ExecuteTool._run
        
        ExecuteTool._run = with_confirmation(ExecuteTool._run)
        
        pica_client = PicaClient(
            secret=get_env_var("PICA_SECRET"),
            options=PicaClientOptions(
                connectors=["*"]
            ),
        )

        pica_client.initialize()

        llm = ChatOpenAI(
            temperature=0,
            model="gpt-4.1",
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()]
        )

        agent = create_pica_agent(
            client=pica_client,
            llm=llm,
            agent_type=AgentType.OPENAI_FUNCTIONS,
        )

        await stream_and_process(
            agent, 
            "Send an email to john@example.com with a funny joke using gmail"
        )

    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")
        sys.exit(1)
    finally:
        # Restore the original ExecuteTool._run method
        ExecuteTool._run = original_run


if __name__ == "__main__":
    asyncio.run(main())
