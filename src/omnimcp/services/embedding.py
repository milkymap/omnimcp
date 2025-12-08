from openai import AsyncOpenAI, AsyncAzureOpenAI
from openai.types.create_embedding_response import CreateEmbeddingResponse
from openai.types.embedding import Embedding

from typing import List, Self, Optional, Union
from ..log import logger

class EmbeddingService:
    def __init__(
        self,
        api_key: str,
        embedding_model_name: str,
        dimension: int,
        # Azure OpenAI settings (optional)
        azure_endpoint: Optional[str] = None,
        azure_api_version: Optional[str] = None,
        azure_embedding_deployment_name: Optional[str] = None,
    ):
        self.api_key = api_key
        self.dimension = dimension

        # Azure configuration
        self.azure_endpoint = azure_endpoint
        self.azure_api_version = azure_api_version

        # Use deployment name for Azure, model name for standard OpenAI
        if azure_endpoint and azure_embedding_deployment_name:
            self.embedding_model_name = azure_embedding_deployment_name
        else:
            self.embedding_model_name = embedding_model_name

    @property
    def is_azure(self) -> bool:
        """Check if Azure OpenAI is configured."""
        return self.azure_endpoint is not None

    async def __aenter__(self) -> Self:
        if self.is_azure:
            self.client: Union[AsyncOpenAI, AsyncAzureOpenAI] = AsyncAzureOpenAI(
                api_key=self.api_key,
                azure_endpoint=self.azure_endpoint,
                api_version=self.azure_api_version,
            )
            logger.info(f"EmbeddingService initialized with Azure OpenAI (deployment: {self.embedding_model_name})")
        else:
            self.client = AsyncOpenAI(api_key=self.api_key)
            logger.info(f"EmbeddingService initialized with OpenAI (model: {self.embedding_model_name})")
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            logger.error(f"Exception in EmbeddingService context manager: {exc_value}")
            logger.exception(traceback)

    async def create_embedding(self, texts: list[str]) -> List[List[float]]:
        # must use tiktoken to estimate token per input... max token per input <= 8192
        # total input tokens per request <= 300_000 tokens 
        # a future implementation must handle chunking of inputs that exceed these limits
        # and batching of requests to stay within rate limits
        response:CreateEmbeddingResponse = await self.client.embeddings.create(
            input=texts,
            model=self.embedding_model_name,
            dimensions=self.dimension
        )
        embeddings = [item.embedding for item in response.data]
        return embeddings
    
    def inject_base_into_corpus(self, base_embedding:List[float], corpus_embeddings:List[List[float]], alpha:float=0.1) -> List[List[float]]:
        beta = 1.0 - alpha
        injected_corpus = []
        
        for corpus_vec in corpus_embeddings:
            # alpha * base + beta * corpus
            injected = [
                alpha * base_embedding[i] + beta * corpus_vec[i] 
                for i in range(len(base_embedding))
            ]
            injected_corpus.append(injected)
        
        return injected_corpus
