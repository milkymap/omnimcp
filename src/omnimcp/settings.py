from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, model_validator


class ApiKeysSettings(BaseSettings):
    # CLI / Server settings
    CONFIG_PATH: str = Field(validation_alias="CONFIG_PATH")
    TRANSPORT: str = Field("http", validation_alias="TRANSPORT")
    HOST: str = Field("localhost", validation_alias="HOST")
    PORT: int = Field(8000, validation_alias="PORT")

    # API Keys
    OPENAI_API_KEY: str = Field(validation_alias="OPENAI_API_KEY")

    # Azure OpenAI settings (optional - when set, enables Azure mode)
    OPENAI_API_ENDPOINT: Optional[str] = Field(default=None, validation_alias="OPENAI_API_ENDPOINT")
    OPENAI_API_VERSION: Optional[str] = Field(default=None, validation_alias="OPENAI_API_VERSION")
    OPENAI_API_LLM_DEPLOYMENT_NAME: Optional[str] = Field(default=None, validation_alias="OPENAI_API_LLM_DEPLOYMENT_NAME")
    OPENAI_API_EMBEDDING_DEPLOYMENT_NAME: Optional[str] = Field(default=None, validation_alias="OPENAI_API_EMBEDDING_DEPLOYMENT_NAME")

    # Model settings (used for standard OpenAI, ignored when Azure is configured)
    DESCRIPTOR_MODEL_NAME: str = Field("gpt-4.1-mini", validation_alias="DESCRIPTOR_MODEL_NAME")
    EMBEDDING_MODEL_NAME: str = Field("text-embedding-3-small", validation_alias="EMBEDDING_MODEL_NAME")
    VISION_MODEL_NAME: str = Field("gpt-4.1-mini", validation_alias="VISION_MODEL_NAME")
    DIMENSIONS: int = Field(1024, validation_alias="DIMENSIONS")

    @property
    def is_azure(self) -> bool:
        """Check if Azure OpenAI is configured."""
        return self.OPENAI_API_ENDPOINT is not None

    @model_validator(mode="after")
    def validate_azure_config(self):
        """Validate Azure OpenAI configuration when endpoint is set."""
        if self.OPENAI_API_ENDPOINT is not None:
            missing = []
            if not self.OPENAI_API_VERSION:
                missing.append("OPENAI_API_VERSION")
            if not self.OPENAI_API_LLM_DEPLOYMENT_NAME:
                missing.append("OPENAI_API_LLM_DEPLOYMENT_NAME")
            if not self.OPENAI_API_EMBEDDING_DEPLOYMENT_NAME:
                missing.append("OPENAI_API_EMBEDDING_DEPLOYMENT_NAME")

            if missing:
                raise ValueError(
                    f"Azure OpenAI endpoint is configured but missing required settings: {', '.join(missing)}.\n"
                    "When using Azure OpenAI, you must provide:\n"
                    "  - OPENAI_API_ENDPOINT (e.g., 'https://your-resource.openai.azure.com')\n"
                    "  - OPENAI_API_VERSION (e.g., '2024-02-15-preview')\n"
                    "  - OPENAI_API_LLM_DEPLOYMENT_NAME (your chat/completion deployment)\n"
                    "  - OPENAI_API_EMBEDDING_DEPLOYMENT_NAME (your embedding deployment)"
                )
        return self

    # Storage settings
    INDEX_NAME: str = Field("omnimcp_idx", validation_alias="INDEX_NAME")
    TOOL_OFFLOADED_DATA_PATH: str = Field(validation_alias="TOOL_OFFLOADED_DATA_PATH")

    # Qdrant connection settings (3 modes: local path, in-memory, or remote URL)
    QDRANT_DATA_PATH: Optional[str] = Field(default=None, validation_alias="QDRANT_DATA_PATH")
    QDRANT_URL: Optional[str] = Field(default=None, validation_alias="QDRANT_URL")
    QDRANT_API_KEY: Optional[str] = Field(default=None, validation_alias="QDRANT_API_KEY")

    @model_validator(mode="after")
    def validate_qdrant_config(self):
        """Validate that exactly one Qdrant connection mode is configured."""
        has_path = self.QDRANT_DATA_PATH is not None
        has_url = self.QDRANT_URL is not None

        if not has_path and not has_url:
            raise ValueError(
                "Qdrant connection not configured. Provide either:\n"
                "  - QDRANT_DATA_PATH for local file storage (e.g., '/path/to/qdrant_data')\n"
                "  - QDRANT_DATA_PATH=':memory:' for in-memory storage\n"
                "  - QDRANT_URL for remote server (Docker or Qdrant Cloud)"
            )

        if has_path and has_url:
            raise ValueError(
                "Cannot use both QDRANT_DATA_PATH and QDRANT_URL. Choose one connection mode:\n"
                "  - QDRANT_DATA_PATH for local/in-memory storage\n"
                "  - QDRANT_URL for remote server"
            )

        if self.QDRANT_API_KEY and not has_url:
            raise ValueError(
                "QDRANT_API_KEY requires QDRANT_URL. "
                "API key authentication is only used with remote Qdrant servers."
            )

        return self

    # Rate limiting
    MCP_SERVER_INDEX_RATE_LIMIT: int = Field(3, validation_alias="MCP_SERVER_INDEX_RATE_LIMIT")
    MCP_SERVER_TOOL_INDEX_RATE_LIMIT: int = Field(32, validation_alias="MCP_SERVER_TOOL_INDEX_RATE_LIMIT")

    # Background queue settings
    BACKGROUND_MCP_TOOL_QUEUE_MAX_SUBSCRIBERS: int = Field(8, validation_alias="BACKGROUND_MCP_TOOL_QUEUE_MAX_SUBSCRIBERS")
    BACKGROUND_MCP_TOOL_QUEUE_SIZE: int = Field(64, validation_alias="BACKGROUND_MCP_TOOL_QUEUE_SIZE")

    # Other settings
    MCP_SERVER_EMBEDDING_WEIGHTS: float = Field(0.1, validation_alias="MCP_SERVER_EMBEDDING_WEIGHTS")
    MCP_SERVER_POLLING_INTERVAL_MS: int = Field(5000, validation_alias="MCP_SERVER_POLLING_INTERVAL_MS")
    MAX_RESULT_TOKENS: int = Field(5000, validation_alias="MAX_RESULT_TOKENS")
    DESCRIBE_IMAGES: bool = Field(True, validation_alias="DESCRIBE_IMAGES")
    
