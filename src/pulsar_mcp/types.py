from pydantic import BaseModel, Field
from typing import Dict, List
from mcp.types import ListToolsResult

class McpStartupConfig(BaseModel):
    command:str
    args: list[str] = Field(default_factory=list)
    env: Dict[str, str] = Field(default_factory=dict)

class McpConfig(BaseModel):
    mcpServers: Dict[str, McpStartupConfig]

class McpServerDescription(BaseModel):
    title: str
    summary: str
    capabilities: List[str]
    limitations: List[str]

class DescribeMcpServerResponse(BaseModel):
    server_name: str
    server_description: McpServerDescription
    tools:ListToolsResult
    