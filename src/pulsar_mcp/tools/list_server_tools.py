import json
from typing import Optional
from fastmcp.tools.tool import ToolResult
from mcp.types import TextContent

from ..mcp_engine import MCPEngine

class ListServerToolsTool:
    def __init__(self, mcp_engine: MCPEngine):
        self.mcp_engine = mcp_engine

    async def __call__(self, server_name: str, limit: int = 50, offset: Optional[str] = None) -> ToolResult:
        return await self.list_server_tools(server_name, limit, offset)

    async def list_server_tools(self, server_name: str, limit: int = 50, offset: Optional[str] = None) -> ToolResult:
        try:
            tools, offset = await self.mcp_engine.index_service.list_tools(
                server_name=server_name,
            )
            if not tools:
                return ToolResult(
                    content=[TextContent(type="text", text=f"No tools found for server '{server_name}'")]
                )

            content = []
            for payload in tools:
                content.append(
                    TextContent(
                        type="text",
                        text=json.dumps({
                            "tool_name": payload.get('tool_name'),
                            "title": payload.get('title')
                        })
                    )
                )

            guidance = "Next steps:\n"
            guidance += f"• Use get_tool_details('{server_name}', 'tool_name') for schema\n"
            guidance += f"• Use manage_server('{server_name}', 'start') before execution\n"
            guidance += "• Always check tool schema before calling execute_tool"
            guidance += f"• Use offset '{offset}' for next page of results" if offset else "Last page of results"
            content.append(TextContent(type="text", text=guidance))
            return ToolResult(content=content)

        except Exception as e:
            return ToolResult(
                content=[TextContent(type="text", text=f"Failed to list tools for server '{server_name}': {str(e)}")]
            )