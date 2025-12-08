import pytest
from src.omnimcp.settings import ApiKeysSettings


class TestApiKeysSettings:
    def test_required_fields(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("QDRANT_DATA_PATH", raising=False)
        monkeypatch.delenv("QDRANT_URL", raising=False)
        monkeypatch.delenv("TOOL_OFFLOADED_DATA_PATH", raising=False)
        monkeypatch.delenv("CONFIG_PATH", raising=False)

        with pytest.raises(Exception):
            ApiKeysSettings()

    def test_minimal_config(self, monkeypatch):
        monkeypatch.setenv("CONFIG_PATH", "/tmp/config.json")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("QDRANT_DATA_PATH", "/tmp/qdrant_data")
        monkeypatch.setenv("TOOL_OFFLOADED_DATA_PATH", "/tmp/tool_offloaded_data")

        settings = ApiKeysSettings()
        assert settings.CONFIG_PATH == "/tmp/config.json"
        assert settings.OPENAI_API_KEY == "sk-test-key"
        assert settings.QDRANT_DATA_PATH == "/tmp/qdrant_data"
        assert settings.TOOL_OFFLOADED_DATA_PATH == "/tmp/tool_offloaded_data"

    def test_default_values(self, monkeypatch):
        monkeypatch.setenv("CONFIG_PATH", "/tmp/config.json")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("QDRANT_DATA_PATH", "/tmp/qdrant_data")
        monkeypatch.setenv("TOOL_OFFLOADED_DATA_PATH", "/tmp/tool_offloaded_data")

        settings = ApiKeysSettings()
        # Server defaults
        assert settings.TRANSPORT == "http"
        assert settings.HOST == "localhost"
        assert settings.PORT == 8000
        # Model defaults
        assert settings.DESCRIPTOR_MODEL_NAME == "gpt-4.1-mini"
        assert settings.EMBEDDING_MODEL_NAME == "text-embedding-3-small"
        assert settings.DIMENSIONS == 1024
        assert settings.INDEX_NAME == "omnimcp_idx"
        assert settings.MAX_RESULT_TOKENS == 5000
        assert settings.DESCRIBE_IMAGES is True
        assert settings.VISION_MODEL_NAME == "gpt-4.1-mini"
        assert settings.MCP_SERVER_INDEX_RATE_LIMIT == 3
        assert settings.MCP_SERVER_TOOL_INDEX_RATE_LIMIT == 32
        assert settings.BACKGROUND_MCP_TOOL_QUEUE_MAX_SUBSCRIBERS == 8
        assert settings.BACKGROUND_MCP_TOOL_QUEUE_SIZE == 64
        # Qdrant defaults
        assert settings.QDRANT_URL is None
        assert settings.QDRANT_API_KEY is None

    def test_custom_values(self, monkeypatch):
        monkeypatch.setenv("CONFIG_PATH", "/custom/config.json")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-custom-key")
        monkeypatch.setenv("QDRANT_DATA_PATH", "/custom/qdrant_data")
        monkeypatch.setenv("TOOL_OFFLOADED_DATA_PATH", "/custom/tool_offloaded_data")
        monkeypatch.setenv("TRANSPORT", "stdio")
        monkeypatch.setenv("HOST", "0.0.0.0")
        monkeypatch.setenv("PORT", "9000")
        monkeypatch.setenv("DESCRIPTOR_MODEL_NAME", "gpt-4o")
        monkeypatch.setenv("EMBEDDING_MODEL_NAME", "text-embedding-3-large")
        monkeypatch.setenv("DIMENSIONS", "3072")
        monkeypatch.setenv("INDEX_NAME", "custom_idx")
        monkeypatch.setenv("MAX_RESULT_TOKENS", "4000")
        monkeypatch.setenv("DESCRIBE_IMAGES", "false")

        settings = ApiKeysSettings()
        assert settings.CONFIG_PATH == "/custom/config.json"
        assert settings.OPENAI_API_KEY == "sk-custom-key"
        assert settings.QDRANT_DATA_PATH == "/custom/qdrant_data"
        assert settings.TOOL_OFFLOADED_DATA_PATH == "/custom/tool_offloaded_data"
        assert settings.TRANSPORT == "stdio"
        assert settings.HOST == "0.0.0.0"
        assert settings.PORT == 9000
        assert settings.DESCRIPTOR_MODEL_NAME == "gpt-4o"
        assert settings.EMBEDDING_MODEL_NAME == "text-embedding-3-large"
        assert settings.DIMENSIONS == 3072
        assert settings.INDEX_NAME == "custom_idx"
        assert settings.MAX_RESULT_TOKENS == 4000
        assert settings.DESCRIBE_IMAGES is False


class TestQdrantConnectionModes:
    def test_qdrant_local_path(self, monkeypatch):
        """Test Qdrant with local file storage."""
        monkeypatch.setenv("CONFIG_PATH", "/tmp/config.json")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("QDRANT_DATA_PATH", "/tmp/qdrant_data")
        monkeypatch.setenv("TOOL_OFFLOADED_DATA_PATH", "/tmp/tool_offloaded_data")

        settings = ApiKeysSettings()
        assert settings.QDRANT_DATA_PATH == "/tmp/qdrant_data"
        assert settings.QDRANT_URL is None
        assert settings.QDRANT_API_KEY is None

    def test_qdrant_in_memory(self, monkeypatch):
        """Test Qdrant with in-memory storage."""
        monkeypatch.setenv("CONFIG_PATH", "/tmp/config.json")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("QDRANT_DATA_PATH", ":memory:")
        monkeypatch.setenv("TOOL_OFFLOADED_DATA_PATH", "/tmp/tool_offloaded_data")

        settings = ApiKeysSettings()
        assert settings.QDRANT_DATA_PATH == ":memory:"
        assert settings.QDRANT_URL is None

    def test_qdrant_remote_url(self, monkeypatch):
        """Test Qdrant with remote URL (Docker/self-hosted)."""
        monkeypatch.setenv("CONFIG_PATH", "/tmp/config.json")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("QDRANT_URL", "http://localhost:6333")
        monkeypatch.setenv("TOOL_OFFLOADED_DATA_PATH", "/tmp/tool_offloaded_data")
        monkeypatch.delenv("QDRANT_DATA_PATH", raising=False)

        settings = ApiKeysSettings()
        assert settings.QDRANT_URL == "http://localhost:6333"
        assert settings.QDRANT_DATA_PATH is None
        assert settings.QDRANT_API_KEY is None

    def test_qdrant_cloud_with_api_key(self, monkeypatch):
        """Test Qdrant Cloud with URL and API key."""
        monkeypatch.setenv("CONFIG_PATH", "/tmp/config.json")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("QDRANT_URL", "https://my-cluster.qdrant.io")
        monkeypatch.setenv("QDRANT_API_KEY", "qdrant-api-key-123")
        monkeypatch.setenv("TOOL_OFFLOADED_DATA_PATH", "/tmp/tool_offloaded_data")
        monkeypatch.delenv("QDRANT_DATA_PATH", raising=False)

        settings = ApiKeysSettings()
        assert settings.QDRANT_URL == "https://my-cluster.qdrant.io"
        assert settings.QDRANT_API_KEY == "qdrant-api-key-123"
        assert settings.QDRANT_DATA_PATH is None

    def test_qdrant_no_connection_fails(self, monkeypatch):
        """Test that missing both QDRANT_DATA_PATH and QDRANT_URL fails."""
        monkeypatch.setenv("CONFIG_PATH", "/tmp/config.json")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("TOOL_OFFLOADED_DATA_PATH", "/tmp/tool_offloaded_data")
        monkeypatch.delenv("QDRANT_DATA_PATH", raising=False)
        monkeypatch.delenv("QDRANT_URL", raising=False)

        with pytest.raises(ValueError, match="Qdrant connection not configured"):
            ApiKeysSettings()

    def test_qdrant_both_path_and_url_fails(self, monkeypatch):
        """Test that providing both QDRANT_DATA_PATH and QDRANT_URL fails."""
        monkeypatch.setenv("CONFIG_PATH", "/tmp/config.json")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("QDRANT_DATA_PATH", "/tmp/qdrant_data")
        monkeypatch.setenv("QDRANT_URL", "http://localhost:6333")
        monkeypatch.setenv("TOOL_OFFLOADED_DATA_PATH", "/tmp/tool_offloaded_data")

        with pytest.raises(ValueError, match="Cannot use both"):
            ApiKeysSettings()

    def test_qdrant_api_key_without_url_fails(self, monkeypatch):
        """Test that QDRANT_API_KEY without QDRANT_URL fails."""
        monkeypatch.setenv("CONFIG_PATH", "/tmp/config.json")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("QDRANT_DATA_PATH", "/tmp/qdrant_data")
        monkeypatch.setenv("QDRANT_API_KEY", "qdrant-api-key-123")
        monkeypatch.setenv("TOOL_OFFLOADED_DATA_PATH", "/tmp/tool_offloaded_data")
        monkeypatch.delenv("QDRANT_URL", raising=False)

        with pytest.raises(ValueError, match="QDRANT_API_KEY requires QDRANT_URL"):
            ApiKeysSettings()


class TestAzureOpenAIConfig:
    """Tests for Azure OpenAI configuration."""

    def _clear_azure_env(self, monkeypatch):
        """Helper to clear Azure-specific env vars."""
        monkeypatch.delenv("OPENAI_API_ENDPOINT", raising=False)
        monkeypatch.delenv("OPENAI_API_VERSION", raising=False)
        monkeypatch.delenv("OPENAI_API_LLM_DEPLOYMENT_NAME", raising=False)
        monkeypatch.delenv("OPENAI_API_EMBEDDING_DEPLOYMENT_NAME", raising=False)

    def test_standard_openai_mode(self, monkeypatch):
        """Test standard OpenAI mode (no Azure settings)."""
        monkeypatch.setenv("CONFIG_PATH", "/tmp/config.json")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("QDRANT_DATA_PATH", "/tmp/qdrant_data")
        monkeypatch.setenv("TOOL_OFFLOADED_DATA_PATH", "/tmp/tool_offloaded_data")
        self._clear_azure_env(monkeypatch)

        settings = ApiKeysSettings()
        assert settings.is_azure is False
        assert settings.OPENAI_API_ENDPOINT is None
        assert settings.OPENAI_API_VERSION is None
        assert settings.OPENAI_API_LLM_DEPLOYMENT_NAME is None
        assert settings.OPENAI_API_EMBEDDING_DEPLOYMENT_NAME is None

    def test_azure_openai_full_config(self, monkeypatch):
        """Test full Azure OpenAI configuration."""
        monkeypatch.setenv("CONFIG_PATH", "/tmp/config.json")
        monkeypatch.setenv("OPENAI_API_KEY", "azure-api-key-123")
        monkeypatch.setenv("QDRANT_DATA_PATH", "/tmp/qdrant_data")
        monkeypatch.setenv("TOOL_OFFLOADED_DATA_PATH", "/tmp/tool_offloaded_data")
        monkeypatch.setenv("OPENAI_API_ENDPOINT", "https://my-resource.openai.azure.com")
        monkeypatch.setenv("OPENAI_API_VERSION", "2024-02-15-preview")
        monkeypatch.setenv("OPENAI_API_LLM_DEPLOYMENT_NAME", "gpt-4-deployment")
        monkeypatch.setenv("OPENAI_API_EMBEDDING_DEPLOYMENT_NAME", "embedding-deployment")

        settings = ApiKeysSettings()
        assert settings.is_azure is True
        assert settings.OPENAI_API_ENDPOINT == "https://my-resource.openai.azure.com"
        assert settings.OPENAI_API_VERSION == "2024-02-15-preview"
        assert settings.OPENAI_API_LLM_DEPLOYMENT_NAME == "gpt-4-deployment"
        assert settings.OPENAI_API_EMBEDDING_DEPLOYMENT_NAME == "embedding-deployment"

    def test_azure_missing_api_version_fails(self, monkeypatch):
        """Test that Azure endpoint without API version fails."""
        monkeypatch.setenv("CONFIG_PATH", "/tmp/config.json")
        monkeypatch.setenv("OPENAI_API_KEY", "azure-api-key-123")
        monkeypatch.setenv("QDRANT_DATA_PATH", "/tmp/qdrant_data")
        monkeypatch.setenv("TOOL_OFFLOADED_DATA_PATH", "/tmp/tool_offloaded_data")
        monkeypatch.setenv("OPENAI_API_ENDPOINT", "https://my-resource.openai.azure.com")
        monkeypatch.setenv("OPENAI_API_LLM_DEPLOYMENT_NAME", "gpt-4-deployment")
        monkeypatch.setenv("OPENAI_API_EMBEDDING_DEPLOYMENT_NAME", "embedding-deployment")
        monkeypatch.delenv("OPENAI_API_VERSION", raising=False)

        with pytest.raises(ValueError, match="OPENAI_API_VERSION"):
            ApiKeysSettings()

    def test_azure_missing_llm_deployment_fails(self, monkeypatch):
        """Test that Azure endpoint without LLM deployment name fails."""
        monkeypatch.setenv("CONFIG_PATH", "/tmp/config.json")
        monkeypatch.setenv("OPENAI_API_KEY", "azure-api-key-123")
        monkeypatch.setenv("QDRANT_DATA_PATH", "/tmp/qdrant_data")
        monkeypatch.setenv("TOOL_OFFLOADED_DATA_PATH", "/tmp/tool_offloaded_data")
        monkeypatch.setenv("OPENAI_API_ENDPOINT", "https://my-resource.openai.azure.com")
        monkeypatch.setenv("OPENAI_API_VERSION", "2024-02-15-preview")
        monkeypatch.setenv("OPENAI_API_EMBEDDING_DEPLOYMENT_NAME", "embedding-deployment")
        monkeypatch.delenv("OPENAI_API_LLM_DEPLOYMENT_NAME", raising=False)

        with pytest.raises(ValueError, match="OPENAI_API_LLM_DEPLOYMENT_NAME"):
            ApiKeysSettings()

    def test_azure_missing_embedding_deployment_fails(self, monkeypatch):
        """Test that Azure endpoint without embedding deployment name fails."""
        monkeypatch.setenv("CONFIG_PATH", "/tmp/config.json")
        monkeypatch.setenv("OPENAI_API_KEY", "azure-api-key-123")
        monkeypatch.setenv("QDRANT_DATA_PATH", "/tmp/qdrant_data")
        monkeypatch.setenv("TOOL_OFFLOADED_DATA_PATH", "/tmp/tool_offloaded_data")
        monkeypatch.setenv("OPENAI_API_ENDPOINT", "https://my-resource.openai.azure.com")
        monkeypatch.setenv("OPENAI_API_VERSION", "2024-02-15-preview")
        monkeypatch.setenv("OPENAI_API_LLM_DEPLOYMENT_NAME", "gpt-4-deployment")
        monkeypatch.delenv("OPENAI_API_EMBEDDING_DEPLOYMENT_NAME", raising=False)

        with pytest.raises(ValueError, match="OPENAI_API_EMBEDDING_DEPLOYMENT_NAME"):
            ApiKeysSettings()

    def test_azure_missing_multiple_fields_lists_all(self, monkeypatch):
        """Test that multiple missing Azure fields are all listed in error."""
        monkeypatch.setenv("CONFIG_PATH", "/tmp/config.json")
        monkeypatch.setenv("OPENAI_API_KEY", "azure-api-key-123")
        monkeypatch.setenv("QDRANT_DATA_PATH", "/tmp/qdrant_data")
        monkeypatch.setenv("TOOL_OFFLOADED_DATA_PATH", "/tmp/tool_offloaded_data")
        monkeypatch.setenv("OPENAI_API_ENDPOINT", "https://my-resource.openai.azure.com")
        self._clear_azure_env(monkeypatch)
        monkeypatch.setenv("OPENAI_API_ENDPOINT", "https://my-resource.openai.azure.com")

        with pytest.raises(ValueError) as exc_info:
            ApiKeysSettings()

        error_msg = str(exc_info.value)
        assert "OPENAI_API_VERSION" in error_msg
        assert "OPENAI_API_LLM_DEPLOYMENT_NAME" in error_msg
        assert "OPENAI_API_EMBEDDING_DEPLOYMENT_NAME" in error_msg
