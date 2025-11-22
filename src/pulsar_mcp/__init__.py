import click 

from pulsar_mcp.log import logger

@click.command()
def main() -> None:
    logger.info("pulsar_mcp main function called.")
    click.echo("Hello from pulsar_mcp!")
