# pica-langchain

[![pypi version](https://img.shields.io/pypi/v/pica-langchain)](https://pypi.org/project/pica-langchain)

<img src="https://assets.picaos.com/github/langchain.svg" alt="Pica LangChain Banner" style="border-radius: 5px;">

A Python package for integrating [Pica](https://picaos.com) with [LangChain](https://langchain.com).

**Full Documentation:** [https://docs.picaos.com/sdk/langchain](https://docs.picaos.com/sdk/langchain)

## Installation

```bash
pip install pica-langchain
```

## Usage

The `PicaClientOptions` class allows you to configure the Pica client with the following options:

| Option | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| server_url | str | No | https://api.picaos.com | URL for self-hosted Pica server. |
| connectors | List[str] | No | [] | List of connector keys to filter by. Pass ["*"] to initialize all available connectors, or specific connector keys to filter. If empty, no connections will be initialized. |
| authkit | bool | No | False | If True, the SDK will use Authkit to connect to prompt the user to connect to a platform that they do not currently have access to |
| identity | str | No | None | Filter connections by specific identity ID. |
| identity_type | "user", "team", "organization", or "project" | No | None | Filter connections by identity type. |

The `create_pica_agent` function allows customizing the following parameters:

| Option | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| verbose | bool | No | False | Whether to print verbose logs. |
| system_prompt | str | No | None | A custom system prompt to append to the default system prompt. |
| agent_type | AgentType | No | OPENAI_FUNCTIONS | The type of agent to create. |
| tools | List[BaseTool] | No | None | A list of tools to use in the agent. |
| return_intermediate_steps | bool | No | False | Whether to return intermediate steps. |

### Quick Start

```python
from langchain_openai import ChatOpenAI
from langchain.agents import AgentType
from pica_langchain import PicaClient, create_pica_agent
from pica_langchain.models import PicaClientOptions

# Initialize the Pica client
pica_client = PicaClient(
    secret="your-pica-secret",
    options=PicaClientOptions(
        # server_url="https://my-self-hosted-server.com",
        # identity_type="user"
        # identity="user-id",
        # authkit=True,

        connectors=["*"] # Initialize all available connections for this example
    )
)

# Create a LangChain agent with Pica tools
llm = ChatOpenAI(
    temperature=0, 
    model="gpt-4o"
)

# Create an agent with Pica tools
agent = create_pica_agent(
    client=pica_client,
    llm=llm,
    agent_type=AgentType.OPENAI_FUNCTIONS,
    # return_intermediate_steps=True, # Optional: Return intermediate steps

    # Optional: Custom system prompt to append
    system_prompt="Always start your response with `Pica works like ✨\n`"
)

# Use the agent
result = agent.invoke({
    "input": (
            "Star the picahq/pica repo in github. "
            "Then, list 5 of the repositories that I have starred in github."
    )
})

print(result)
```

### Using Individual Tools

```python
from langchain.agents import AgentType, initialize_agent
from langchain_openai import ChatOpenAI
from pica_langchain import PicaClient, create_pica_tools

# Initialize the Pica client
pica_client = PicaClient(secret="your-pica-secret")

# Create Pica tools
tools = create_pica_tools(pica_client)

# Create a custom agent with the tools
llm = ChatOpenAI(temperature=0, model="gpt-4o")
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.OPENAI_FUNCTIONS
)

# Use the agent
result = agent.run("What actions are available in Gmail?")
print(result)
```
### Using Model Context Protocol (MCP) Tools

The SDK supports integration with [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) servers, allowing you to connect to external tool providers via the MCP protocol.

```python
import asyncio
from langchain.agents import AgentType
from langchain_openai import ChatOpenAI
from pica_langchain import PicaClient, create_pica_agent
from pica_langchain.models import PicaClientOptions

# Configure MCP servers
mcp_options = {
    "math": {
        "command": "python",
        "args": ["./path/to/math_server.py"],
        "transport": "stdio",
    },
    "weather": {
        "url": "http://localhost:8000/sse",
        "transport": "sse",
    }
}

async def main():
    # Create client with async initialization
    pica_client = await PicaClient.create(
        secret="your-pica-secret",
        options=PicaClientOptions(
            connectors=["*"],  # Initialize all available connections
            mcp_options=mcp_options,  # Add MCP server options
        ),
    )

    # Create an agent with both Pica and MCP tools
    llm = ChatOpenAI(temperature=0, model="gpt-4o")
    agent = create_pica_agent(
        client=pica_client,
        llm=llm,
        agent_type=AgentType.OPENAI_FUNCTIONS,
    )

    # Use both Pica platform actions and MCP tools
    result = await agent.ainvoke({
        "input": "Calculate 25 * 17, then check the weather in New York, finally list all connectors Pica supported"
    })
    
    print(result["output"])

if __name__ == "__main__":
    asyncio.run(main())
```

## Development

### Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/pica-langchain.git
cd pica-langchain
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

3. Create a connection on [Pica](https://app.picaos.com):

```bash
1. Create an account on app.picaos.com.
2. Navigate to the "My Connections" tab and create the required connection.
3. Retrieve your API Key from the "API Keys" section.
```

4. Export required environment variables:

```bash
export PICA_SECRET="your-pica-secret"
export OPENAI_API_KEY="your-openai-api-key"
```

5. Install development dependencies:

```bash
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Logging

The Pica LangChain SDK uses the `logging` module to log messages. The log level can be set using the `PICA_LOG_LEVEL` environment variable.

The following log levels are available:

- `debug`
- `info`
- `warning`
- `error`
- `critical`

```bash
export PICA_LOG_LEVEL="debug"
```

### Examples

Examples can be found in the [examples](examples) directory.

```bash
> python3 examples/use_with_langchain.py # LangChain agent example
```

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).
