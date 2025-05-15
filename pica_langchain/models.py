from typing import Dict, List, Any, Optional, Union, Literal
from pydantic import BaseModel, Field, ConfigDict

class SupportedFilter(BaseModel):
    key: str
    operators: List[str]

    model_config = ConfigDict(
        populate_by_name=True,
    )


class OAuthSettings(BaseModel):
    enabled: bool
    scopes: str


class ConnectionData(BaseModel):
    type: str
    platform: str
    status: str
    supported_actions: List[str] = Field(alias="supportedActions")
    oauth: OAuthSettings
    pagination: bool
    filtration: bool
    sorting: bool
    caveats: List[str]
    supported_filters: List[SupportedFilter] = Field(alias="supportedFilters")
    supported_sort_keys: Optional[List[str]] = Field(alias="supportedSortKeys")
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )


class ManageEntityParams(BaseModel):
    operation: Literal['list', 'get', 'create', 'update', 'delete', 'count', 'capabilities']
    entity_type: str = Field(alias="entityType")
    connection_key: str = Field(alias="connectionKey")
    id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )


class AvailableAction(BaseModel):
    """Model for an available action."""
    _id: Optional[str] = None
    title: Optional[str] = None
    connection_platform: Optional[str] = Field(None, alias="connectionPlatform")
    knowledge: Optional[str] = None
    path: Optional[str] = None
    base_url: Optional[str] = Field(None, alias="baseUrl")
    tags: Optional[List[str]] = Field(default_factory=list)
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra='allow'
    )


class RequestConfig(BaseModel):
    url: str
    method: Optional[str] = None
    headers: Dict[str, Union[str, int, bool]]
    params: Optional[Dict[str, Union[str, int, bool]]] = None
    data: Optional[Any] = None
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )


class FrontendSpec(BaseModel):
    title: str
    description: str
    platform: str
    category: str
    image: str
    tags: List[str]


class ConnectionForm(BaseModel):
    name: str
    description: str
    form_data: List[Any] = Field(alias="formData")
    
    model_config = ConfigDict(
        populate_by_name=True
    )


class Frontend(BaseModel):
    spec: FrontendSpec
    connection_form: ConnectionForm = Field(alias="connectionForm")
    
    model_config = ConfigDict(
        populate_by_name=True
    )


class Paths(BaseModel):
    id: str
    event: str
    payload: Any
    timestamp: str
    secret: str
    signature: str
    cursor: str


class Settings(BaseModel):
    parse_webhook_body: bool = Field(alias="parseWebhookBody")
    show_secret: bool = Field(alias="showSecret")
    allow_custom_events: bool = Field(alias="allowCustomEvents")
    oauth: bool
    
    model_config = ConfigDict(
        populate_by_name=True
    )


class ConnectionDefinition(BaseModel):
    """Model for a connection definition."""
    _id: Optional[str] = None
    name: str
    key: str
    platform: str
    platform_version: str = Field(alias="platformVersion")
    description: Optional[str] = None
    category: Optional[str] = None
    image: Optional[str] = None
    tags: Optional[List[str]] = None
    oauth: Optional[bool] = None
    created_at: int = Field(alias="createdAt")
    updated_at: int = Field(alias="updatedAt")
    updated: bool
    version: str
    last_modified_by: str = Field(alias="lastModifiedBy")
    deleted: bool
    active: bool
    deprecated: bool
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="allow"
    )


class Connection(BaseModel):
    """Model for a connection."""
    _id: str
    platform_version: str = Field(alias="platformVersion")
    connectionDefinitionId: Optional[str] = None
    name: Optional[str] = None
    key: str
    environment: str
    platform: str
    secretsServiceId: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    throughput: Optional[Dict[str, Any]] = None
    created_at: int = Field(alias="createdAt")
    updated_at: int = Field(alias="updatedAt")
    updated: bool
    version: str
    last_modified_by: str = Field(alias="lastModifiedBy")
    deleted: bool
    change_log: Optional[List[Dict[str, Any]]] = None
    tags: Optional[List[str]] = None
    active: bool
    deprecated: bool
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="allow"
    )


class ActionToExecute(BaseModel):
    id: str = Field(alias="_id")
    path: str

    model_config = ConfigDict(
        populate_by_name=True
    )


class ExecuteParams(BaseModel):
    platform: str
    action: ActionToExecute
    method: str
    connection_key: str
    data: Optional[Dict[str, Any]] = None
    path_variables: Optional[Dict[str, Any]] = None
    query_params: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, Any]] = None
    is_form_data: bool = False
    is_url_encoded: bool = False
    
    model_config = ConfigDict(
        populate_by_name=True
    )


class PicaResponse(BaseModel):
    success: bool
    content: Optional[str] = None
    message: Optional[str] = None
    raw: Optional[str] = None
    title: Optional[str] = None
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )


class ActionsResponse(PicaResponse):
    actions: Optional[List[Dict[str, Any]]] = None
    platform: Optional[str] = None


class ActionKnowledgeResponse(PicaResponse):
    success: bool
    platform: str
    action: Optional[AvailableAction] = None


class ExecuteResponse(PicaResponse):
    data: Optional[Any] = None
    connection_key: Optional[str] = Field(alias="connectionKey", default=None)
    platform: Optional[str] = None
    action: Optional[str] = None
    request_config: Optional[RequestConfig] = Field(alias="requestConfig", default=None)
    knowledge: Optional[str] = None
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )


class PicaClientOptions(BaseModel):
    """Configuration options for the Pica client."""
    server_url: str = Field(
        default="https://api.picaos.com",
        description="Custom server URL to use instead of the default"
    )
    connectors: List[str] = Field(
        default_factory=list,
        description="List of connector keys to filter by. Use [\"*\"] to initialize all connections."
    )
    identity: Optional[str] = Field(
        default=None,
        description="Filter connections by specific identity ID"
    )
    identity_type: Optional[Literal["user", "team", "organization", "project"]] = Field(
        default=None,
        description="Filter connections by identity type (user, team, organization, or project)"
    )
    authkit: bool = Field(
        default=False,
        description="Whether to use the AuthKit integration which enables the promptToConnectPlatform tool"
    )
    mcp_options: Optional[Dict[str, Any]] = Field(
        default=None,
        description="MCP server configuration options. Dictionary with server names as keys and configuration as values."
    )    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )