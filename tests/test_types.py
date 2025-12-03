import pytest
from pydantic import ValidationError
from src.omnimcp.types import (
    McpStartupConfig,
    McpServersConfig,
    McpServerDescription,
    McpServerToolDescription,
)


class TestMcpStartupConfigStdio:
    """Tests for stdio transport configuration."""

    def test_minimal_stdio_config(self):
        config = McpStartupConfig(command="npx")
        assert config.command == "npx"
        assert config.args == []
        assert config.env == {}
        assert config.timeout == 30.0
        assert config.overwrite is False
        assert config.ignore is False
        assert config.hints is None
        assert config.blocked_tools is None
        assert config.transport == "stdio"

    def test_full_stdio_config(self):
        config = McpStartupConfig(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem"],
            env={"HOME": "/home/user"},
            timeout=60.0,
            overwrite=True,
            ignore=False,
            hints=["file operations", "read/write"],
            blocked_tools=["delete_file", "execute_command"]
        )
        assert config.command == "npx"
        assert config.args == ["-y", "@modelcontextprotocol/server-filesystem"]
        assert config.env == {"HOME": "/home/user"}
        assert config.timeout == 60.0
        assert config.overwrite is True
        assert config.hints == ["file operations", "read/write"]
        assert config.blocked_tools == ["delete_file", "execute_command"]
        assert config.transport == "stdio"

    def test_blocked_tools_list(self):
        config = McpStartupConfig(
            command="test",
            blocked_tools=["tool1", "tool2", "tool3"]
        )
        assert "tool1" in config.blocked_tools
        assert "tool2" in config.blocked_tools
        assert "tool4" not in config.blocked_tools

    def test_ignore_flag(self):
        config = McpStartupConfig(command="test", ignore=True)
        assert config.ignore is True

    def test_overwrite_flag(self):
        config = McpStartupConfig(command="test", overwrite=True)
        assert config.overwrite is True


class TestMcpStartupConfigHttp:
    """Tests for HTTP transport configuration."""

    def test_minimal_http_config(self):
        config = McpStartupConfig(url="http://localhost:8000/mcp")
        assert config.url == "http://localhost:8000/mcp"
        assert config.headers == {}
        assert config.timeout == 30.0
        assert config.transport == "http"

    def test_full_http_config(self):
        config = McpStartupConfig(
            url="https://api.example.com/mcp",
            headers={"Authorization": "Bearer token123", "X-Custom": "value"},
            timeout=120.0,
            overwrite=True,
            hints=["remote API", "cloud service"],
            blocked_tools=["dangerous_tool"]
        )
        assert config.url == "https://api.example.com/mcp"
        assert config.headers == {"Authorization": "Bearer token123", "X-Custom": "value"}
        assert config.timeout == 120.0
        assert config.overwrite is True
        assert config.hints == ["remote API", "cloud service"]
        assert config.blocked_tools == ["dangerous_tool"]
        assert config.transport == "http"

    def test_http_config_with_empty_headers(self):
        config = McpStartupConfig(url="http://localhost:8000/mcp", headers={})
        assert config.headers == {}
        assert config.transport == "http"


class TestMcpStartupConfigValidation:
    """Tests for transport configuration validation."""

    def test_error_when_both_url_and_command(self):
        with pytest.raises(ValidationError) as exc_info:
            McpStartupConfig(
                command="npx",
                url="http://localhost:8000/mcp"
            )
        assert "Cannot specify both 'url' and 'command'" in str(exc_info.value)

    def test_error_when_neither_url_nor_command(self):
        with pytest.raises(ValidationError) as exc_info:
            McpStartupConfig(timeout=30.0)
        assert "Must specify either 'url'" in str(exc_info.value)

    def test_transport_property_stdio(self):
        config = McpStartupConfig(command="uvx")
        assert config.transport == "stdio"

    def test_transport_property_http(self):
        config = McpStartupConfig(url="http://localhost:8000/mcp")
        assert config.transport == "http"


class TestMcpStartupConfigBackwardsCompatibility:
    """Tests to ensure backwards compatibility with existing configs."""

    def test_existing_config_format_still_works(self):
        """Existing configs without 'url' field should still work."""
        config = McpStartupConfig(
            command="uvx",
            args=["mcp-fetch"],
            env={"API_KEY": "secret"}
        )
        assert config.command == "uvx"
        assert config.args == ["mcp-fetch"]
        assert config.transport == "stdio"

    def test_json_dict_parsing_stdio(self):
        """Test parsing from dict (simulating JSON config)."""
        config_dict = {
            "command": "npx",
            "args": ["-y", "some-package"],
            "timeout": 45.0
        }
        config = McpStartupConfig(**config_dict)
        assert config.command == "npx"
        assert config.transport == "stdio"

    def test_json_dict_parsing_http(self):
        """Test parsing from dict (simulating JSON config)."""
        config_dict = {
            "url": "http://remote-server:8080/mcp",
            "headers": {"Authorization": "Bearer xyz"},
            "timeout": 60.0
        }
        config = McpStartupConfig(**config_dict)
        assert config.url == "http://remote-server:8080/mcp"
        assert config.transport == "http"


class TestMcpServersConfig:
    def test_empty_config(self):
        config = McpServersConfig(mcpServers={})
        assert config.mcpServers == {}

    def test_single_server(self):
        config = McpServersConfig(
            mcpServers={
                "filesystem": McpStartupConfig(command="npx", args=["-y", "fs-server"])
            }
        )
        assert "filesystem" in config.mcpServers
        assert config.mcpServers["filesystem"].command == "npx"

    def test_multiple_servers(self):
        config = McpServersConfig(
            mcpServers={
                "filesystem": McpStartupConfig(command="npx"),
                "github": McpStartupConfig(command="uvx", blocked_tools=["delete_repo"]),
                "ignored": McpStartupConfig(command="test", ignore=True)
            }
        )
        assert len(config.mcpServers) == 3
        assert config.mcpServers["github"].blocked_tools == ["delete_repo"]
        assert config.mcpServers["ignored"].ignore is True

    def test_mixed_transport_servers(self):
        """Test configuration with both stdio and http servers."""
        config = McpServersConfig(
            mcpServers={
                "local-fs": McpStartupConfig(command="npx", args=["-y", "fs-server"]),
                "remote-api": McpStartupConfig(
                    url="http://api.example.com/mcp",
                    headers={"Authorization": "Bearer token"}
                ),
                "local-github": McpStartupConfig(command="uvx", args=["mcp-github"]),
            }
        )
        assert len(config.mcpServers) == 3
        assert config.mcpServers["local-fs"].transport == "stdio"
        assert config.mcpServers["remote-api"].transport == "http"
        assert config.mcpServers["local-github"].transport == "stdio"
        assert config.mcpServers["remote-api"].headers == {"Authorization": "Bearer token"}

    def test_config_from_json_dict_mixed(self):
        """Test parsing full config from dict (simulating JSON file)."""
        config_dict = {
            "mcpServers": {
                "fetch": {
                    "command": "uvx",
                    "args": ["mcp-fetch"],
                    "timeout": 30
                },
                "cloud-service": {
                    "url": "https://mcp.cloud.example.com/api",
                    "headers": {"X-API-Key": "secret-key"},
                    "timeout": 60
                }
            }
        }
        config = McpServersConfig(**config_dict)
        assert config.mcpServers["fetch"].transport == "stdio"
        assert config.mcpServers["fetch"].command == "uvx"
        assert config.mcpServers["cloud-service"].transport == "http"
        assert config.mcpServers["cloud-service"].url == "https://mcp.cloud.example.com/api"


class TestMcpServerDescription:
    def test_description(self):
        desc = McpServerDescription(
            title="Filesystem Server",
            summary="Provides file system operations",
            capabilities=["read files", "write files", "list directories"],
            limitations=["no network access", "sandboxed paths"]
        )
        assert desc.title == "Filesystem Server"
        assert len(desc.capabilities) == 3
        assert len(desc.limitations) == 2


class TestMcpServerToolDescription:
    def test_tool_description(self):
        desc = McpServerToolDescription(
            title="Read File Tool",
            summary="Reads content from a file",
            utterances=["read the file", "get file content", "show me the file"]
        )
        assert desc.title == "Read File Tool"
        assert len(desc.utterances) == 3
