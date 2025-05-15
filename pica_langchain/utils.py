import warnings
from typing import List, Optional, Dict, Any, Union


from langchain_core._api.deprecation import LangChainDeprecationWarning
from langchain.tools import BaseTool
from langchain.agents import AgentType, initialize_agent
from langchain.llms.base import BaseLLM
from langchain.chat_models.base import BaseChatModel

from .client import PicaClient
from .tools import (
    GetAvailableActionsTool,
    GetActionKnowledgeTool,
    ExecuteTool,
    PromptToConnectPlatformTool,
)

from .logger import get_logger

warnings.filterwarnings("ignore", category=LangChainDeprecationWarning)

logger = get_logger()

def create_pica_tools(client: PicaClient) -> List[BaseTool]:
    """
    Create a list of Pica tools for use with LangChain.

    Args:
        client: The Pica client to use.

    Returns:
        A list of LangChain tools.
    """
    tools: List[BaseTool] = [
        GetAvailableActionsTool(client=client),
        GetActionKnowledgeTool(client=client),
        ExecuteTool(client=client),
    ]

    # Add the PromptToConnectPlatformTool if AuthKit is enabled
    if hasattr(client, "_use_authkit") and client._use_authkit:
        tools.append(PromptToConnectPlatformTool(client=client))

    return tools


def get_tools_from_client(client: PicaClient) -> List[BaseTool]:
    """
    Get all tools from a Pica client, including both Pica tools and MCP tools.

    Args:
        client: The Pica client to use.

    Returns:
        A list of LangChain tools.
    """
    # Get standard Pica tools
    pica_tools = create_pica_tools(client)

    # Get MCP tools if available
    mcp_tools = client.get_mcp_tools() if hasattr(client, "get_mcp_tools") else []

    # Combine all tools
    return pica_tools + mcp_tools


def create_pica_agent(
    client: PicaClient,
    llm: Union[BaseLLM, BaseChatModel],
    agent_type: AgentType = AgentType.OPENAI_FUNCTIONS,
    verbose: bool = False,
    agent_kwargs: Optional[Dict[str, Any]] = None,
    system_prompt: Optional[str] = None,
    tools: Optional[List[BaseTool]] = None,
    **kwargs,
):
    """
    Create a LangChain agent with Pica tools.

    Args:
        client: The Pica client to use.
        llm: The language model to use.
        agent_type: The type of agent to create.
        verbose: Whether to enable verbose output.
        agent_kwargs: Additional arguments for the agent.
        system_prompt: Optional custom system prompt to prepend to the Pica system prompt.
        tools: Optional list of additional tools to include alongside the Pica tools.
        **kwargs: Additional arguments for initialize_agent.

    Returns:
        A LangChain agent.
    """
    import asyncio

    # Create default Pica tools
    all_tools = get_tools_from_client(client)

    # Combine default tools with any user-provided tools
    if tools:
        all_tools = all_tools + tools

    # Generate system prompt with Pica information
    if system_prompt:
        try:
            loop = asyncio.get_running_loop()
            # We're in an event loop, use the client.system property directly
            # and append the user system prompt
            combined_system_prompt = client.system
            if system_prompt:
                from .prompts import generate_full_system_prompt

                combined_system_prompt = generate_full_system_prompt(
                    combined_system_prompt, system_prompt
                )
        except RuntimeError:
            # No running event loop, safe to use asyncio.run()
            combined_system_prompt = asyncio.run(
                client.generate_system_prompt(system_prompt)
            )
    else:
        # If no custom prompt, use the default system prompt
        combined_system_prompt = client.system

    default_agent_kwargs = {"system_message": combined_system_prompt}

    # Merge default agent kwargs with user-provided ones
    if agent_kwargs:
        default_agent_kwargs.update(agent_kwargs)

    # Create and return the agent
    return initialize_agent(
        all_tools,
        llm,
        agent=agent_type,
        verbose=verbose,
        agent_kwargs=default_agent_kwargs,
        **kwargs,
    )
