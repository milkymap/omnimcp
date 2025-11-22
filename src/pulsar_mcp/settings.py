from pydantic_settings import BaseSettings
from pydantic import Field


class ApiKeysSettings(BaseSettings):
    OPENAI_API_KEY: str = Field(validation_alias="OPENAI_API_KEY")
    DESCRIPTOR_MODEL_NAME:str = Field("gpt-4.1-mini", validation_alias="DESCRIPTOR_MODEL_NAME")
    EMBEDDING_MODEL_NAME:str = Field("text-embedding-3-small", validation_alias="EMBEDDING_MODEL_NAME")
    DIMENSIONS:int = Field(1024, validation_alias="DIMENSIONS")
    INDEX_NAME: str = Field("pulsar_idx", validation_alias="INDEX_NAME")
    QDRANT_STORAGE_PATH: str = Field(validation_alias="QDRANT_STORAGE_PATH")
    THREAD_POOL_MAX_WORKERS:int = Field(32, validation_alias="THREAD_POOL_MAX_WORKERS")
    MCP_SERVER_STARTUP_TIMEOUT:int = Field(30, validation_alias="MCP_SERVER_STARTUP_TIMEOUT")
