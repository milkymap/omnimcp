from pulsar_mcp import main 
"""
Stage 1 - Explore (2 tools):
- semantic_search → Find relevant tools/servers
- list_indexed_servers → Browse available servers

Stage 2 - Investigate (3 tools):
- get_server_info → Server capabilities/limitations
- list_server_tools → Tool names from server
- get_tool_details → Full tool schema when needed

Stage 3 - Execute (3 tools):
- manage_server → Start/stop servers
- list_running_servers → Check active sessions
- execute_tool → Run tools
"""

if __name__ == '__main__':
    main()