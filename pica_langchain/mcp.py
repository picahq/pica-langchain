from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.sse import sse_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
    AsyncCallbackManagerForToolRun,
)
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
            # Create wrapped tools that establish connections on each use
            self._tools = await self.create_wrapped_mcp_tools(self.options.servers)
            logger.info(f"Loaded {len(self._tools)} wrapped MCP tools")

            # Add detailed logging for each tool
            for tool in self._tools:
                logger.info(f"Loaded MCP tool: {tool.name} - {tool.description}")
            
            logger.info(f"Loaded {len(self._tools)} wrapped MCP tools")
            return self._tools
        except Exception as e:
            logger.error(f"Error initializing MCP client: {e}")
            return []

    async def create_wrapped_mcp_tools(
        self, server_configs: Dict[str, Dict[str, Any]]
    ) -> List[BaseTool]:
        """
        Create session-aware MCP tools that establish a fresh connection on each call.
        
        Args:
            server_configs: Dictionary of server configurations.
            
        Returns:
            List of session-aware MCP tools.
        """
        wrapped_tools = []
        
        for server_name, config in server_configs.items():
            try:
                # Connect once to get tool definitions
                tools = await connect_to_single_server(config)
                
                for tool in tools:
                    # Get parameter schema in a safe way that handles different versions
                    if hasattr(tool, 'args_schema'):
                        schema_obj = tool.args_schema
                        # Try different methods to get the schema
                        if hasattr(schema_obj, 'model_json_schema'):
                            # Newer Pydantic v2
                            param_schema = schema_obj.model_json_schema()
                        elif hasattr(schema_obj, 'schema'):
                            # Older Pydantic v1
                            param_schema = schema_obj.schema()
                        elif isinstance(schema_obj, dict):
                            # Direct dictionary
                            param_schema = schema_obj
                    
                    # Create a wrapped version of each tool
                    wrapped_tool = SessionAwareMCPToolWrapper(
                        name=tool.name,
                        description=tool.description,
                        server_config=config,
                        func_name=tool.name,
                        parameter_schema=param_schema
                    )
                    
                    wrapped_tools.append(wrapped_tool)
                    
            except Exception as e:
                logger.error(f"Error loading tools from {server_name}: {e}")
                
        return wrapped_tools

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


async def connect_to_single_server(server_config: Dict[str, Any]) -> List[BaseTool]:
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
        logger.debug(f"Starting subprocess with command: {command} {' '.join(args)}")

        async with stdio_client(server_params) as (read, write):
            logger.debug("Stdio client connected, initializing session")
            async with ClientSession(read, write) as session:
                logger.debug("Session initialized, loading tools")
                await session.initialize()
                tools = await load_mcp_tools(session)
                tool_names = [tool.name for tool in tools]
                logger.info(f"Loaded tools: {tool_names}")
                return tools

    elif transport == "sse":
        url = server_config.get("url")

        if not url:
            raise ValueError("URL is required for SSE transport")

        try:
            async def execute_tool():
                async with sse_client(url) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        tools = await load_mcp_tools(session)
                        tool_names = [tool.name for tool in tools]
                        logger.info(f"Loaded tools: {tool_names}")
                        return tools

            return await asyncio.wait_for(execute_tool(), timeout=10)  # 10 second timeout

        except asyncio.TimeoutError:
            error_msg = f"Timeout while connecting to MCP server: {server_config.get('name', 'unknown')}"
            logger.error(error_msg)
            return []

    elif transport == "streamable_http":
        url = server_config.get("url")

        if not url:
            raise ValueError("URL is required for streamable HTTP transport")

        try:
            async def execute_tool():
                async with streamablehttp_client(url) as (read, write, _):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        tools = await load_mcp_tools(session)
                        tool_names = [tool.name for tool in tools]
                        logger.info(f"Loaded tools: {tool_names}")
                        return tools

            return await asyncio.wait_for(execute_tool(), timeout=10)  # 10 second timeout

        except asyncio.TimeoutError:
            error_msg = f"Timeout while connecting to MCP server: {server_config.get('name', 'unknown')}"
            logger.error(error_msg)
            return []

    else:
        raise ValueError(f"Unsupported transport: {transport}")


class SessionAwareMCPToolWrapper(BaseTool):
    name: str
    description: str
    server_config: Dict[str, Any]
    func_name: str
    parameter_schema: Dict[str, Any] = {}
    
    def _run(self, **kwargs: Any) -> Any:
        """Synchronous run - not supported for MCP tools"""
        raise NotImplementedError("MCP tools only support async execution")
        
    async def _arun(self, **kwargs: Any) -> Any:
        """Execute the tool asynchronously by creating a fresh session."""
        logger.info(f"Executing MCP tool: {self.name} with args: {kwargs}")
        try:
            # Get transport config
            transport = self.server_config.get("transport", "stdio")
            
            if transport == "stdio":
                command = self.server_config.get("command")
                args = self.server_config.get("args", [])
                
                if not command:
                    raise ValueError("Command is required for stdio transport")

                # Use asyncio.wait_for for timeout handling
                try:
                    async def execute_tool():
                        server_params = StdioServerParameters(command=command, args=args)
                        logger.debug(f"Starting subprocess with command: {command} {' '.join(args)}")
                        
                        async with stdio_client(server_params) as (read, write):
                            logger.debug("Stdio client connected, initializing session")
                            async with ClientSession(read, write) as session:
                                await session.initialize()
                                logger.debug("Session initialized")
                                
                                # Directly call the tool using the session
                                arguments = kwargs
                                logger.debug(f"Calling {self.func_name} with arguments: {arguments}")
                                result = await session.call_tool(self.func_name, arguments)
                                logger.info(f"Tool execution successful, result: {result}")
                                return result
                                
                    return await asyncio.wait_for(execute_tool(), timeout=10)  # 10 second timeout
                    
                except asyncio.TimeoutError:
                    error_msg = f"Timeout while executing MCP tool {self.name}"
                    logger.error(error_msg)
                    return error_msg
                                
            elif transport == "sse":
                url = self.server_config.get("url")
                
                if not url:
                    raise ValueError("URL is required for SSE transport")
                
                try:
                    async def execute_tool():
                        async with sse_client(url) as (read, write):
                            async with ClientSession(read, write) as session:
                                await session.initialize()
                                arguments = kwargs
                                logger.debug(f"Calling {self.func_name} with arguments: {arguments}")
                                result = await session.call_tool(self.func_name, arguments)
                                logger.info(f"Tool execution successful, result: {result}")
                                return result
                    
                    return await asyncio.wait_for(execute_tool(), timeout=10)  # 10 second timeout
                    
                except asyncio.TimeoutError:
                    error_msg = f"Timeout while executing MCP tool {self.name}"
                    logger.error(error_msg)
                    return error_msg
                        
            elif transport == "streamable_http":
                url = self.server_config.get("url")
                
                if not url:
                    raise ValueError("URL is required for streamable HTTP transport")
                
                try:
                    async def execute_tool():
                        async with streamablehttp_client(url) as (read, write, _):
                            async with ClientSession(read, write) as session:
                                await session.initialize()
                                arguments = kwargs
                                logger.debug(f"Calling {self.func_name} with arguments: {arguments}")
                                result = await session.call_tool(self.func_name, arguments)
                                logger.info(f"Tool execution successful, result: {result}")
                                return result
                    
                    return await asyncio.wait_for(execute_tool(), timeout=10)  # 10 second timeout
                    
                except asyncio.TimeoutError:
                    error_msg = f"Timeout while executing MCP tool {self.name}"
                    logger.error(error_msg)
                    return error_msg
            else:
                raise ValueError(f"Unsupported transport: {transport}")
                
        except Exception as e:
            error_msg = f"Error executing MCP tool {self.name}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return error_msg