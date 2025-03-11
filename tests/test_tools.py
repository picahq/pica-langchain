import unittest
from unittest.mock import MagicMock
import json

from pica_langchain.client import PicaClient
from pica_langchain.tools import GetAvailableActionsTool, GetActionKnowledgeTool, ExecuteTool
from pica_langchain.models import ActionsResponse, ActionKnowledgeResponse, ExecuteResponse, AvailableAction

class TestPicaTools(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock(spec=PicaClient)
        
        self.mock_actions_response = ActionsResponse(
            success=True,
            actions=[{"_id": "action1", "title": "Test Action", "tags": ["test"]}],
            platform="gmail",
            content="Found 1 available actions for gmail"
        )
        self.mock_knowledge_response = ActionKnowledgeResponse(
            success=True,
            action=AvailableAction(
                _id="action1",
                title="Test Action",
                connectionPlatform="gmail",
                knowledge="This is a test action",
                path="/test/path",
                baseUrl="https://api.example.com",
                tags=["test"]
            ),
            platform="gmail",
            content="Found knowledge for action: Test Action"
        )
        
        self.mock_execute_response = ExecuteResponse(
            success=True,
            data={"result": "success"},
            connectionKey="test-conn-1",
            platform="gmail", 
            action="Test Action",
            content="Executed Test Action via gmail"
        )
        
        self.mock_client.get_available_actions.return_value = self.mock_actions_response
        self.mock_client.get_action_knowledge.return_value = self.mock_knowledge_response
        self.mock_client.execute.return_value = self.mock_execute_response
    
    def test_get_available_actions_tool(self):
        tool = GetAvailableActionsTool(
            client=self.mock_client
        )
        
        result = tool._run("gmail")
        
        self.mock_client.get_available_actions.assert_called_once_with("gmail")
        
        result_dict = json.loads(result)
        self.assertTrue(result_dict["success"])
        self.assertEqual(result_dict["platform"], "gmail")
        self.assertEqual(len(result_dict["actions"]), 1)
        self.assertEqual(result_dict["actions"][0]["_id"], "action1")
    
    def test_get_action_knowledge_tool(self):
        tool = GetActionKnowledgeTool(
            client=self.mock_client
        )
        
        result = tool._run("gmail", "action1")
        
        self.mock_client.get_action_knowledge.assert_called_once_with("gmail", "action1")
        
        result_dict = json.loads(result)
        self.assertTrue(result_dict["success"])
        self.assertEqual(result_dict["platform"], "gmail")
        self.assertEqual(result_dict["action"]["_id"], "action1")
        self.assertEqual(result_dict["action"]["title"], "Test Action")
    
    def test_execute_tool(self):
        tool = ExecuteTool(
            client=self.mock_client
        )
        
        result = tool._run(
            platform="gmail",
            action_id="action1",
            action_path="/test/path",
            method="GET",
            connection_key="test-conn-1",
            data={"param": "value"}
        )
        
        result_dict = json.loads(result)
        self.assertTrue(result_dict["success"])
        self.assertEqual(result_dict["platform"], "gmail")
        self.assertEqual(result_dict["connection_key"], "test-conn-1")
        self.assertEqual(result_dict["data"], {"result": "success"})

if __name__ == '__main__':
    unittest.main()
