from contextlib import asynccontextmanager
from fastmcp import FastMCP
from typing import Optional 

from .mcp_engine import MCPEngine
from .settings import ApiKeysSettings
from .log import logger

class MCPServer:
    def __init__(self, api_keys_settings:ApiKeysSettings, mcp_config_filepath:str):
        self.api_keys_settings = api_keys_settings
        self.mcp_config_filepath = mcp_config_filepath
        self.mcp = FastMCP(
            name="pulsar_mcp",
            instructions="An advanced MCP server powered by Pulsar MCP.",
            lifespan=self.lifespan
        )
    
    async def run_server(self):
        await self.mcp.run_async(transport="stdio")

    @asynccontextmanager
    async def lifespan(self, mcp:FastMCP):
        async with MCPEngine(self.api_keys_settings) as mcp_engine:
            try:
                mcp_config = mcp_engine.load_mcp_config(self.mcp_config_filepath)
                mcp_engine.mcp_config = mcp_config
                await mcp_engine.index_mcp_servers(mcp_config)
            except Exception as e:
                logger.error(f"Failed to load/index MCP config: {e}")

            self.define_tools(mcp, mcp_engine)
            yield

    def define_tools(self, mcp:FastMCP, mcp_engine:MCPEngine):
        @mcp.tool(
            name="semantic_search",
            description="Search for MCP servers or tools using natural language queries."
        )
        async def semantic_search(query: str, limit: int = 10, scope: Optional[str] = None, server_names: list[str] = None):
            """
            Search for MCP servers or tools.

            Args:
                query: Natural language description of what you're looking for
                scope: Optional scope filter "server", "tool"
                limit: Maximum number of results to return (default: 10)
                server_names: Optional list of server names to filter by, use this only when scope = tool.
            Returns:
                List of matching results with relevance scores
            """
            try:

                enhanced_query = await mcp_engine.descriptor_service.enhance_query_with_llm(query)
                query_embedding = await mcp_engine.embedding_service.create_embedding([enhanced_query])

                all_results = await mcp_engine.index_service.search(
                    query_embedding=query_embedding[0],
                    top_k=limit,
                    server_names=server_names,
                    scope=scope
                )
                minimal_results = []
                for result in all_results:
                    payload = result.get('payload', {})
                    if payload.get('type') == 'server':
                        minimal_results.append({
                            "type": "server",
                            "server_name": payload.get('server_name'),
                            "title": payload.get('title'),
                            "score": result.get('score', 0)
                        })
                    elif payload.get('type') == 'tool':
                        minimal_results.append({
                            "type": "tool",
                            "server_name": payload.get('server_name'),
                            "tool_name": payload.get('tool_name'),
                            "score": result.get('score', 0)
                        })

                return {
                    "query": query,
                    "scope": scope,
                    "results": minimal_results,
                    "total_found": len(minimal_results)
                }

            except Exception as e:
                return {
                    "error": f"Search failed: {str(e)}",
                    "original_query": query,
                    "scope": scope
                }

        @mcp.tool(
            name="get_server_info",
            description="Get detailed information about a specific MCP server."
        )
        async def get_server_info(server_name: str):
            """
            Get server details including capabilities and limitations.

            Args:
                server_name: Name of the MCP server

            Returns:
                Full server information from index
            """
            try:
                server_info = await mcp_engine.index_service.get_server(server_name)

                if server_info is None:
                    return {
                        "error": f"Server '{server_name}' not found",
                        "server_name": server_name
                    }

                return {
                    "server_name": server_name,
                    "server_info": server_info
                }

            except Exception as e:
                return {
                    "error": f"Failed to get server info: {str(e)}",
                    "server_name": server_name
                }

        @mcp.tool(
            name="list_indexed_servers",
            description="List all currently indexed MCP servers with minimal info."
        )
        async def list_indexed_servers(limit: int = 20, offset: Optional[str] = None):
            """
            List all indexed MCP servers.

            Args:
                limit: Maximum number of servers to return (default: 20)
                offset: Offset for pagination. first call should be None.

            Returns:
                List of servers with minimal payload (name, title, tool count)
            """
            try:
                servers = await mcp_engine.index_service.list_servers(
                    limit=limit,
                    offset=offset
                )
                total_servers = await mcp_engine.index_service.nb_servers()

                minimal_servers = []
                for payload in servers:
                    minimal_servers.append({
                        "server_name": payload.get('server_name'),
                        "title": payload.get('title'),
                        "nb_tools": payload.get('nb_tools', 0)
                    })

                return {
                    "servers": minimal_servers,
                    "total_servers": total_servers,
                    "limit": limit,
                    "offset": offset
                }

            except Exception as e:
                return {
                    "error": f"Failed to list servers: {str(e)}"
                }

        @mcp.tool(
            name="list_server_tools",
            description="List tool names available on a specific MCP server."
        )
        async def list_server_tools(server_name: str):
            """
            List tool names from a specific server.

            Args:
                server_name: Name of the MCP server

            Returns:
                List of tool names only (minimal payload)
            """
            try:
                tools = await mcp_engine.index_service.list_tools(
                    server_names=[server_name]
                )

                tool_names = []
                for payload in tools:
                    tool_names.append(payload.get('tool_name'))
                    
                return {
                    "server_name": server_name,
                    "tool_names": tool_names,
                    "total_tools": len(tool_names)
                }

            except Exception as e:
                return {
                    "error": f"Failed to list tools for server '{server_name}': {str(e)}",
                    "server_name": server_name
                }


        @mcp.tool(
            name="get_tool_details",
            description="""Get detailed information about a specific tool by name and server.
            This provides comprehensive details about a tool including its schema and enhanced description.
            """
        )
        async def get_tool_details(tool_name: str, server_name: str):
            """
            Get detailed information about a specific tool.

            Args:
                tool_name: Name of the tool
                server_name: Name of the server that provides the tool

            Returns:
                Detailed tool information including schema and description
            """
            try:
                tool_info = await mcp_engine.index_service.get_tool(
                    server_name=server_name,
                    tool_name=tool_name
                )

                if tool_info is None:
                    return {
                        "error": f"Tool '{tool_name}' not found on server '{server_name}'",
                        "tool_name": tool_name,
                        "server_name": server_name
                    }

                return {
                    "tool_name": tool_name,
                    "server_name": server_name,
                    "tool_info": tool_info
                }

            except Exception as e:
                return {
                    "error": f"Failed to get tool details: {str(e)}",
                    "tool_name": tool_name,
                    "server_name": server_name
                }

        @mcp.tool(
            name="manage_server",
            description="Start or shutdown an MCP server."
        )
        async def manage_server(server_name: str, action: str):
            """
            Manage MCP server lifecycle.

            Args:
                server_name: Name of the MCP server
                action: "start" or "shutdown"

            Returns:
                Server status and operation result
            """
            try:
                match action:
                    case "start":
                        success = await mcp_engine.start_mcp_server(server_name)
                        status = "running" if success else "failed"
                    case "shutdown":
                        success = await mcp_engine.shutdown_mcp_server(server_name)
                        status = "shutdown" if success else "failed"
                    case _:
                        return {
                            "server_name": server_name,
                            "success": False,
                            "error": f"Invalid action: {action}. Use 'start' or 'shutdown'."
                        }
                return {
                    "server_name": server_name,
                    "action": action,
                    "success": success,
                    "status": status
                }
            except Exception as e:
                return {
                    "server_name": server_name,
                    "action": action,
                    "success": False,
                    "error": str(e)
                }

        @mcp.tool(
            name="list_running_servers",
            description="List all currently running MCP servers."
        )
        async def list_running_servers():
            try:
                running_servers = mcp_engine.list_running_servers()
                return {
                    "running_servers": running_servers,
                    "total_running": len(running_servers)
                }
            except Exception as e:
                return {
                    "error": str(e)
                }

        @mcp.tool(
            name="execute_tool",
            description="Execute a tool on a running MCP server."
        )
        async def execute_tool(server_name: str, tool_name: str, arguments: dict = None):
            try:
                if arguments is None:
                    arguments = {}
                result = await mcp_engine.execute_tool(server_name, tool_name, arguments)
                return result
            except Exception as e:
                return {
                    "success": False,
                    "server_name": server_name,
                    "tool_name": tool_name,
                    "error": str(e)
                } 
            