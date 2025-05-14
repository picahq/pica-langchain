from typing import Dict, Any, List, Optional, Union
import asyncio
from contextlib import asynccontextmanager

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.sse import sse_client

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.tools import BaseTool

from .logger import get_logger

logger = get_logger()

class MCPClientOptions:
    """Configuration options for MCP client."""
    
    def __init__(
        self,
        servers: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        """
        Initialize MCP client options.
        
        Args:
            servers: Dictionary of server configurations.
                Each server config should have:
                - transport: "stdio", "sse", or "streamable_http"
                - For stdio: "command" and "args"
                - For sse/streamable_http: "url"
        """
        self.servers = servers or {}


class PicaMCPClient:
    """Client for interacting with MCP servers."""
    
    def __init__(self, options: Optional[MCPClientOptions] = None):
        """
        Initialize the MCP client.
        
        Args:
            options: Optional configuration parameters.
        """
        self.options = options or MCPClientOptions()
        self._client = None
        self._tools = []
        self._session = None
        
    async def initialize(self) -> List[BaseTool]:
        """
        Initialize connections to MCP servers and load tools.
        
        Returns:
            List of LangChain tools from MCP servers.
        """
        if not self.options.servers:
            logger.warning("No MCP servers configured")
            return []
            
        try:
            # Store the client in the instance to keep the connection alive
            self._client = MultiServerMCPClient(self.options.servers)
            # Open the connection and keep it open
            await self._client.__aenter__()
            # Get the tools
            self._tools = self._client.get_tools()
            logger.info(f"Loaded {len(self._tools)} tools from MCP servers")
            return self._tools
        except Exception as e:
            logger.error(f"Error initializing MCP client: {e}")
            # Clean up if there was an error
            if self._client:
                try:
                    await self._client.__aexit__(None, None, None)
                except Exception:
                    pass
            return []
            
    def get_tools(self) -> List[BaseTool]:
        """
        Get the loaded MCP tools.
        
        Returns:
            List of LangChain tools from MCP servers.
        """
        return self._tools
        
    @asynccontextmanager
    async def connect(self):
        """
        Context manager for connecting to MCP servers.
        
        Yields:
            The MCP client instance.
        """
        if not self.options.servers:
            logger.warning("No MCP servers configured")
            yield self
            return
            
        try:
            async with MultiServerMCPClient(self.options.servers) as client:
                self._client = client
                self._tools = client.get_tools()
                logger.info(f"Connected to MCP servers with {len(self._tools)} tools")
                yield self
        except Exception as e:
            logger.error(f"Error connecting to MCP servers: {e}")
            yield self


async def connect_to_single_server(
    server_config: Dict[str, Any]
) -> List[BaseTool]:
    """
    Connect to a single MCP server and load its tools.
    
    Args:
        server_config: Server configuration with transport and connection details.
        
    Returns:
        List of LangChain tools from the MCP server.
    """
    transport = server_config.get("transport", "stdio")
    
    if transport == "stdio":
        command = server_config.get("command")
        args = server_config.get("args", [])
        
        if not command:
            raise ValueError("Command is required for stdio transport")
            
        server_params = StdioServerParameters(command=command, args=args)
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return await load_mcp_tools(session)
                
    elif transport == "sse":
        url = server_config.get("url")
        
        if not url:
            raise ValueError("URL is required for SSE transport")
            
        async with sse_client(url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return await load_mcp_tools(session)
                
    elif transport == "streamable_http":
        url = server_config.get("url")
        
        if not url:
            raise ValueError("URL is required for streamable HTTP transport")
            
        async with streamablehttp_client(url) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return await load_mcp_tools(session)
                
    else:
        raise ValueError(f"Unsupported transport: {transport}")
