import os
import pytest
from pica_langchain import PicaClient, create_pica_tools

if not os.environ.get("PICA_SECRET"):
    print("ERROR: PICA_SECRET environment variable must be set to run integration tests")
    print("Skipping integration tests...")

@pytest.mark.skipif(not os.environ.get("PICA_SECRET"), reason="PICA_SECRET not set")
class TestIntegration:
    """Integration tests that require a real Pica API secret."""
    
    @pytest.fixture
    def client(self):
        return PicaClient(secret=os.environ["PICA_SECRET"])
    
    def test_create_tools(self, client):
        tools = create_pica_tools(client)
        assert len(tools) == 3
        assert tools[0].name == "get_available_actions"
        assert tools[1].name == "get_action_knowledge"
        assert tools[2].name == "execute"
    
    def test_get_available_actions(self, client):
        tools = create_pica_tools(client)
        get_actions_tool = tools[0]
        
        result = get_actions_tool.run("github")
        import json
        data = json.loads(result)
        
        assert data["success"] is True
        assert data["platform"] == "github"
        assert isinstance(data["actions"], list) 