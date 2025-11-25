from fastmcp.tools.tool import ToolResult
from mcp.types import TextContent

from ..mcp_engine import MCPEngine

class GetToolDetailsTool:
    def __init__(self, mcp_engine: MCPEngine):
        self.mcp_engine = mcp_engine

    async def __call__(self, tool_name: str, server_name: str) -> ToolResult:
        return await self.get_tool_details(tool_name, server_name)

    async def get_tool_details(self, tool_name: str, server_name: str) -> ToolResult:
        try:
            tool_info = await self.mcp_engine.index_service.get_tool(
                server_name=server_name,
                tool_name=tool_name
            )

            if tool_info is None:
                return ToolResult(
                    content=[TextContent(type="text", text=f"Tool '{tool_name}' not found on server '{server_name}'")]
                )

            details = f"Tool: {tool_name} (from {server_name})\n\n"
            details += f"Description: {tool_info.get('tool_description', 'No description available')}\n\n"
            details += f"Schema:\n{tool_info.get('tool_schema', 'No schema available')}\n"

            guidance = "IMPORTANT: Review this schema carefully before execution!\n\n"
            guidance += "Next steps:\n"
            guidance += f"Ensure server is running: manage_server('{server_name}', 'start')\n"
            guidance += f"Execute: execute_tool('{server_name}', '{tool_name}', arguments)\n"
            guidance += "Always provide correct arguments matching the schema above"
            guidance += "For long running tool, consider to launch them in background and poll for results."

            return ToolResult(
                content=[
                    TextContent(type="text", text=details),
                    TextContent(type="text", text=guidance)
                ]
            )

        except Exception as e:
            return ToolResult(
                content=[TextContent(type="text", text=f"Failed to get tool details: {str(e)}")]
            )