"""
Example demonstrating basic usage of the Pica LangChain tools.
"""

import os
import sys
from pica_langchain import PicaClient, create_pica_tools
from pica_langchain.models import PicaClientOptions


def main():
    pica_secret = os.environ.get("PICA_SECRET")

    if not pica_secret:
        print("ERROR: PICA_SECRET environment variable must be set")
        sys.exit(1)

    client = PicaClient(
        secret=pica_secret,
        options=PicaClientOptions(
            connectors=["*"]
        )
    )

    # Create LangChain tools
    tools = create_pica_tools(client)
    print(f"Created {len(tools)} Pica tools")

    # Test the get_available_actions tool
    get_actions_tool = tools[0]

    try:
        actions = get_actions_tool.run("gmail")

        print(f"\nAvailable Gmail actions:\n{actions}")
    except Exception as e:
        print(f"Error getting Gmail actions: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
