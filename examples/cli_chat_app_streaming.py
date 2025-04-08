"""
CLI-based chat application example using pica-langchain with streaming responses.
This example creates an interactive chat session in the terminal with streaming responses.
"""

import os
import sys
import time
from typing import Optional, Generator, Dict, Any

from langchain_openai import ChatOpenAI
from langchain.agents import AgentType
from langchain.schema import LLMResult
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema.output import GenerationChunk

from pica_langchain import PicaClient, create_pica_agent
from pica_langchain.models import PicaClientOptions


class CliStreamingHandler(BaseCallbackHandler):
    """Custom callback handler for streaming text in the CLI with a typing effect."""
    
    def __init__(self, typing_speed: float = 0.01):
        """Initialize with optional typing speed (delay between characters)."""
        self.typing_speed = typing_speed
    
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Callback for when new token is received in a token-wise streaming setting."""
        print(token, end="", flush=True)
        time.sleep(self.typing_speed)
    
    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        """Callback for when LLM ends generating."""
        print("\n")
    
    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs) -> None:
        """Callback for when chain starts running."""
        print("\n🤖 Thinking...\n", flush=True)


def get_env_var(name: str) -> str:
    """Get environment variable or exit if not set."""
    value = os.environ.get(name)

    if not value:
        print(f"ERROR: {name} environment variable must be set")
        sys.exit(1)

    return value


def process_user_input(agent, user_input: str) -> None:
    """Process user input and stream the response."""
    print("\n🤖 Response:", end=" ", flush=True)
    
    try:
        for chunk in agent.stream({"input": user_input}):
            pass
    except Exception as e:
        print(f"\n❌ Error: {e}")


def main():
    """Main function to run the CLI chat application."""
    print("🤖 Welcome to Pica CLI Chat! (Type 'exit' to quit)")
    print("-------------------------------------------")
    
    try:
        # Initialize the Pica client
        pica_client = PicaClient(
            secret=get_env_var("PICA_SECRET"),
            options=PicaClientOptions(
                connectors=["*"],  # Initialize all available connections
            )
        )
        
        llm_with_handler = ChatOpenAI(
            temperature=0,
            model="gpt-4o",
            streaming=True,
            callbacks=[CliStreamingHandler(typing_speed=0.005)]
        )

        agent = create_pica_agent(
            client=pica_client,
            llm=llm_with_handler,
            agent_type=AgentType.OPENAI_FUNCTIONS,
        )
        
        print("\n🤖 Hi! I'm your Pica-powered assistant. How can I help you today?")
        
        while True:
            user_input = input("\n🧑 You: ")
            
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("\n🤖 Goodbye! Thanks for chatting.")
                break
                
            process_user_input(agent, user_input)
            
    except KeyboardInterrupt:
        print("\n\n🤖 Chat session ended by user.")
    except Exception as e:
        print(f"\n❌ ERROR: An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
