from pydantic import BaseModel, Field, model_validator
from typing import Dict, List, Optional, Literal, Self


class McpStartupConfig(BaseModel):
    # stdio transport fields (for local subprocess)
    command: Optional[str] = None
    args: list[str] = Field(default_factory=list)
    env: Dict[str, str] = Field(default_factory=dict)

    # http transport fields (for remote server)
    url: Optional[str] = None
    headers: Dict[str, str] = Field(default_factory=dict)

    # shared fields
    timeout: float = 30.0
    overwrite: bool = False  # if true, re-index even if already indexed
    ignore: bool = False  # do not index this, or if exists, filter out during search. has more priority than overwrite
    hints: Optional[List[str]] = None
    blocked_tools: Optional[List[str]] = None  # tools that cannot be executed at runtime

    @property
    def transport(self) -> Literal["stdio", "http"]:
        """Auto-detect transport based on config fields."""
        return "http" if self.url else "stdio"

    @model_validator(mode="after")
    def validate_transport_config(self) -> Self:
        if self.url and self.command:
            raise ValueError("Cannot specify both 'url' and 'command' - choose one transport type")
        if not self.url and not self.command:
            raise ValueError("Must specify either 'url' (for http transport) or 'command' (for stdio transport)")
        return self

class McpServersConfig(BaseModel):
    mcpServers: Dict[str, McpStartupConfig]

class McpServerDescription(BaseModel):
    title: str = Field(description="A short, descriptive technical title for the MCP server")
    summary: str = Field(description="A brief summary of the MCP server's purpose and functionality")
    capabilities: List[str] = Field(description="A list of key capabilities and features of the MCP server")
    limitations: List[str] = Field(description="A list of known limitations or constraints of the MCP server")

class McpServerToolDescription(BaseModel):
    title: str = Field(description="A short, descriptive technical title for the tool")
    summary: str = Field(description="A brief summary of the tool's purpose and functionality")
    utterances: List[str] = Field(description="Example utterances or commands that can be used to invoke the tool")

    