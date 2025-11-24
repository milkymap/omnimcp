import asyncio 
import click 

from pulsar_mcp.log import logger
from pulsar_mcp.settings import ApiKeysSettings
from pulsar_mcp.mcp_engine import MCPEngine
from pulsar_mcp.mcp_server import MCPServer

from pulsar_mcp.utilities import load_mcp_config
from dotenv import load_dotenv

@click.command()
@click.option(
    '--mcp-config-filepath', 
    type=click.Path(exists=True, dir_okay=False, readable=True), 
    required=True,
    help='Path to the MCP server configuration file(Claude Code JSON Format).'
)
@click.option("--transport", type=click.Choice(["stdio", "http"]), default="stdio", help="Transport method to communicate with MCP server.")
@click.option("--host", type=str, default="localhost", help="Host for HTTP transport (if applicable).")
@click.option("--port", type=int, default=8000, help="Port for HTTP transport (if applicable).")
def main(mcp_config_filepath:str, transport:str, host:str, port:int) -> None:
    load_dotenv()
    api_keys_settings = ApiKeysSettings() # Load settings to ensure environment variables are read
    mcp_config = load_mcp_config(mcp_config_filepath)  # Validate config file early

    async def async_main():
        logger.info("pulsar_mcp main function called.")
        
        async with MCPEngine(
            api_keys_settings=api_keys_settings,
            mcp_config=mcp_config
        ) as mcp_engine:
            await mcp_engine.index_mcp_servers()
            logger.info("MCP Engine initialized successfully.")
            mcp_server = MCPServer(mcp_engine=mcp_engine)
            await mcp_server.run_server(
                transport=transport,
                host=host,
                port=port
            )
        
    asyncio.run(async_main())
        