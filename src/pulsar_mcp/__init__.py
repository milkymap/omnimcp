import asyncio
import click

from pulsar_mcp.log import logger
from pulsar_mcp.settings import ApiKeysSettings
from pulsar_mcp.mcp_engine import MCPEngine
from pulsar_mcp.mcp_server import MCPServer
from pulsar_mcp.utilities import load_mcp_config
from dotenv import load_dotenv


@click.group()
def cli():
    """Pulsar MCP - Semantic router for MCP ecosystems"""
    pass


@cli.command()
@click.option(
    '--config',
    type=click.Path(exists=True, dir_okay=False, readable=True),
    required=True,
    help='Path to the MCP server configuration file.'
)
def index(config: str) -> None:
    """Index MCP servers for semantic search."""
    load_dotenv()
    api_keys_settings = ApiKeysSettings()
    mcp_config = load_mcp_config(config)

    async def async_index():
        logger.info("Starting indexing...")
        async with MCPEngine(
            api_keys_settings=api_keys_settings,
            mcp_config=mcp_config,
            mode="index"
        ) as mcp_engine:
            await mcp_engine.index_mcp_servers()
        logger.info("Indexing completed.")

    asyncio.run(async_index())


@cli.command()
@click.option(
    '--config',
    type=click.Path(exists=True, dir_okay=False, readable=True),
    required=True,
    help='Path to the MCP server configuration file.'
)
@click.option("--transport", type=click.Choice(["stdio", "http"]), default="stdio", help="Transport method.")
@click.option("--host", type=str, default="localhost", help="Host for HTTP transport.")
@click.option("--port", type=int, default=8000, help="Port for HTTP transport.")
def serve(config: str, transport: str, host: str, port: int) -> None:
    """Start the MCP server (requires prior indexing)."""
    load_dotenv()
    api_keys_settings = ApiKeysSettings()
    mcp_config = load_mcp_config(config)

    async def async_serve():
        logger.info("Starting server...")
        async with MCPEngine(
            api_keys_settings=api_keys_settings,
            mcp_config=mcp_config,
            mode="serve"
        ) as mcp_engine:
            mcp_server = MCPServer(mcp_engine=mcp_engine)
            await mcp_server.run_server(
                transport=transport,
                host=host,
                port=port
            )

    asyncio.run(async_serve())


@cli.command()
@click.option(
    '--config',
    type=click.Path(exists=True, dir_okay=False, readable=True),
    required=True,
    help='Path to the MCP server configuration file.'
)
@click.option("--transport", type=click.Choice(["stdio", "http"]), default="stdio", help="Transport method.")
@click.option("--host", type=str, default="localhost", help="Host for HTTP transport.")
@click.option("--port", type=int, default=8000, help="Port for HTTP transport.")
def run(config: str, transport: str, host: str, port: int) -> None:
    """Index and serve in one command."""
    load_dotenv()
    api_keys_settings = ApiKeysSettings()
    mcp_config = load_mcp_config(config)

    async def async_run():
        # Index first
        logger.info("Starting indexing...")
        async with MCPEngine(
            api_keys_settings=api_keys_settings,
            mcp_config=mcp_config,
            mode="index"
        ) as mcp_engine:
            await mcp_engine.index_mcp_servers()
        logger.info("Indexing completed.")

        # Then serve
        logger.info("Starting server...")
        async with MCPEngine(
            api_keys_settings=api_keys_settings,
            mcp_config=mcp_config,
            mode="serve"
        ) as mcp_engine:
            mcp_server = MCPServer(mcp_engine=mcp_engine)
            await mcp_server.run_server(
                transport=transport,
                host=host,
                port=port
            )

    asyncio.run(async_run())


def main():
    cli()
