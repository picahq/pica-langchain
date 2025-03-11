# pica-langchain

A Python package for integrating [Pica](https://picaos.com) with [LangChain](https://langchain.com).

Full Documentation: [https://docs.picaos.com/sdk/langchain](https://docs.picaos.com/sdk/langchain)

## Installation

```bash
pip install pica-langchain
```

## Usage

### PicaClientOptions

The `PicaClientOptions` class allows you to configure the Pica client with the following options:

| Option | Type | Description |
|--------|------|-------------|
| `server_url` | `str` | Optional URL for self-hosted Pica server. Defaults to `https://api.picaos.com`. |
| `connectors` | `List[str]` | Optional list of connector keys to give the LLM access to. If not provided, all available connectors will be initialized. |


### Quick Start

```python
from langchain_openai import ChatOpenAI
from langchain.agents import AgentType
from pica_langchain import PicaClient, create_pica_agent
from pica_langchain.models import PicaClientOptions

# Initialize the Pica client
pica_client = PicaClient(secret="your-pica-secret")

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
    verbose=True,  # Set to False to hide verbose agent logs

    # Optional: Custom system prompt to append
    system_prompt="Always start your response with `Pica works like ✨\n`"
)

# Use the agent
result = agent.invoke({
    "input": (
        "Star the picahq/pica repo in github. "
        "Then, list the number of stars for the picahq/pica repo in github."
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
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)

# Use the agent
result = agent.run("What actions are available in Gmail?")
print(result)
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
source venv/bin/activate  # On Windows: venv\Scripts\activate
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

### Examples

Examples can be found in the [examples](examples) directory.

```bash
> python3 examples/use_with_langchain.py # LangChain agent example
```

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).
