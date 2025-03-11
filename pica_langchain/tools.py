from typing import Dict, Any, Optional, ClassVar
from langchain.tools import BaseTool
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
import json
from pydantic import BaseModel, Field

from .client import PicaClient
from .models import ExecuteParams, ActionToExecute
from .logger import get_logger

logger = get_logger()

class GetAvailableActionsTool(BaseTool):
    """Tool for getting available actions for a platform."""
    
    name: ClassVar[str] = "get_available_actions"
    description: ClassVar[str] = "Get available actions for a platform"
    client: PicaClient
    
    def _run(
        self, 
        platform: str, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """
        Run the tool to get available actions.
        
        Args:
            platform: The platform to get actions for.
            run_manager: Callback manager for the tool run.
            
        Returns:
            JSON string with the available actions.
        """
        logger.info(f"Getting available actions for platform: {platform}")
        response = self.client.get_available_actions(platform)
        logger.debug(f"Got response with {len(response.actions or [])} actions")

        return json.dumps(response.model_dump(), default=str)
    
    async def _arun(
        self, 
        platform: str, 
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """
        Async version of the run method.
        """
        return self._run(platform=platform)


class GetActionKnowledgeTool(BaseTool):
    """Tool for getting knowledge about a specific action."""
    
    name: ClassVar[str] = "get_action_knowledge"
    description: ClassVar[str] = "Get full action details including knowledge documentation for a specific action"
    client: PicaClient
    
    def _run(
        self, 
        platform: str,
        action_id: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """
        Run the tool to get action knowledge.
        
        Args:
            platform: The platform the action belongs to.
            action_id: The ID of the action.
            run_manager: Callback manager for the tool run.
            
        Returns:
            JSON string with the action knowledge.
        """
        logger.info(f"Getting knowledge for action ID: {action_id} on platform: {platform}")
        response = self.client.get_action_knowledge(platform, action_id)
        
        if response.success:
            logger.debug(f"Successfully retrieved knowledge for action: {response.action.title if response.action else 'unknown'}")
        else:
            logger.warning(f"Failed to get knowledge for action ID: {action_id}: {response.message}")
        
        return json.dumps(response.model_dump(), default=str)
    
    async def _arun(
        self, 
        platform: str,
        action_id: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """
        Async version of the run method.
        """
        return self._run(platform=platform, action_id=action_id)


class ExecuteTool(BaseTool):
    """Tool for executing a specific action using the passthrough API."""
    
    name: ClassVar[str] = "execute"
    description: ClassVar[str] = "Execute a specific action using the passthrough API"
    client: PicaClient
    
    def _run(
        self, 
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
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """
        Run the tool to execute an action.
        
        Args:
            platform: The platform to execute the action on.
            action_id: The ID of the action to execute.
            action_path: The path of the action to execute.
            method: The HTTP method to use.
            connection_key: The connection key to use.
            data: Optional data to send with the request.
            path_variables: Optional variables to replace in the path.
            query_params: Optional query parameters to include in the request.
            headers: Optional headers to include in the request.
            is_form_data: Whether to send the data as form data.
            is_url_encoded: Whether to send the data as url encoded.
            run_manager: Callback manager for the tool run.
            
        Returns:
            JSON string with the execution results.
        """
        logger.info(f"Executing action ID: {action_id} on platform: {platform} with method: {method}")
        
        action = ActionToExecute(_id=action_id, path=action_path)

        params = ExecuteParams(
            platform=platform,
            action=action,
            method=method,
            connection_key=connection_key,
            data=data,
            path_variables=path_variables,
            query_params=query_params,
            headers=headers,
            is_form_data=is_form_data,
            is_url_encoded=is_url_encoded
        )
        
        response = self.client.execute(params)

        if response.success:
            logger.info(f"Successfully executed action: {response.action} on platform: {platform}")
        else:
            logger.warning(f"Failed to execute action: {response.message}")
        
        return json.dumps(response.model_dump(), default=str)
    
    async def _arun(
        self, 
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
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """
        Async version of the run method.
        """

        return self._run(
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
            is_url_encoded=is_url_encoded
        )

class GetAvailableActionsSchema(BaseModel):
    platform: str = Field(description="The platform to get available actions for")

class GetActionKnowledgeSchema(BaseModel):
    platform: str = Field(description="The platform the action belongs to")
    action_id: str = Field(description="The ID of the action to get knowledge for")

class ExecuteSchema(BaseModel):
    platform: str = Field(description="The platform to execute the action on")
    action_id: str = Field(description="The ID of the action to execute")
    action_path: str = Field(description="The path of the action to execute")
    method: str = Field(description="The HTTP method to use (GET, POST, PUT, DELETE, etc.)")
    connection_key: str = Field(description="The connection key to use")
    data: Optional[Dict[str, Any]] = Field(None, description="Optional data to send with the request")
    path_variables: Optional[Dict[str, Any]] = Field(None, description="Optional variables to replace in the path")
    query_params: Optional[Dict[str, Any]] = Field(None, description="Optional query parameters to include in the request")
    headers: Optional[Dict[str, Any]] = Field(None, description="Optional headers to include in the request")
    is_form_data: bool = Field(False, description="Whether to send the data as form data")
    is_url_encoded: bool = Field(False, description="Whether to send the data as url encoded")

GetAvailableActionsTool.args_schema = GetAvailableActionsSchema
GetActionKnowledgeTool.args_schema = GetActionKnowledgeSchema
ExecuteTool.args_schema = ExecuteSchema
