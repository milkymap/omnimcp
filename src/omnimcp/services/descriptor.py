import json
import asyncio

from openai import AsyncOpenAI, AsyncAzureOpenAI
from openai.types.chat import ParsedChatCompletion
from typing import List, Dict, Any, Self, Optional, Union

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from ..types import McpServerDescription, McpServerToolDescription
from ..log import logger

class DescriptorService:
    def __init__(
        self,
        openai_api_key: str,
        openai_model_name: str,
        # Azure OpenAI settings (optional)
        azure_endpoint: Optional[str] = None,
        azure_api_version: Optional[str] = None,
        azure_llm_deployment_name: Optional[str] = None,
    ):
        self.api_key = openai_api_key

        # Azure configuration
        self.azure_endpoint = azure_endpoint
        self.azure_api_version = azure_api_version

        # Use deployment name for Azure, model name for standard OpenAI
        if azure_endpoint and azure_llm_deployment_name:
            self.openai_model_name = azure_llm_deployment_name
        else:
            self.openai_model_name = openai_model_name

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
            logger.info(f"DescriptorService initialized with Azure OpenAI (deployment: {self.openai_model_name})")
        else:
            self.client = AsyncOpenAI(api_key=self.api_key)
            logger.info(f"DescriptorService initialized with OpenAI (model: {self.openai_model_name})")
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            logger.error(f"Exception in EmbeddingService context manager: {exc_value}")
            logger.exception(traceback)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True
    )
    async def enhance_query_with_llm(self, query: str) -> str:
        prompt = f"""You are a query enhancement system for semantic tool search.
        Each tool is a function with specific input and output types, a defined process, and a clear purpose.
        Transform this user query into a detailed technical description that will match tool documentation better.
        Example of tools: web_search, file reader, audio processing etc...
        Our index contains several tools(thousands) with various capabilities.

        User Query: "{query}"

        Instructions:
        1. Identify the implicit conversion or transformation needed
        2. Make explicit: input type, output type, process, and purpose
        3. Add relevant technical terms and synonyms
        4. Expand to 60-100 words
        5. DO NOT mention specific tools or brands
        6. Focus on capabilities and processes

        Enhanced Query (single paragraph, no explanations):"""
        completion_response = await self.client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model=self.openai_model_name,
            max_tokens=384
        )
        enhanced = completion_response.choices[0].message.content.strip()
        
        return enhanced

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True
    )
    async def describe_mcp_server_tool(self, tool_name: str, tool_description: str, tool_schema: Dict[str, Any], server_name: str) -> McpServerToolDescription:
        system_prompt = """
        Generate a comprehensive tool description for semantic search and retrieval with:
        - title: Clear, specific technical title
        - summary: detailed paragraph summarizing the tool's purpose and functionality
        - utterances: 5-7 example commands or queries that would invoke this tool    
        Be specific, clear, and include relevant keywords for search matching."""
        user_prompt = f"""Server: {server_name}
        Tool Name: {tool_name}
        Description: {tool_description}
        Schema: {json.dumps(tool_schema, indent=2)}
        Generate the enhanced description.
        """

        completion_response = await self.client.beta.chat.completions.parse(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model=self.openai_model_name,
            max_tokens=1024,
            response_format=McpServerToolDescription
        )
        enhanced_tool:McpServerToolDescription = completion_response.choices[0].message.parsed
        return enhanced_tool
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True
    )
    async def describe_mcp_server(self, server_name:str, enhanced_tools:List[McpServerToolDescription]) -> McpServerDescription:
        system_prompt = """
        Generate a concise MCP server description with:
        - title: Clear, specific sentence that describes the server
        - summary: detailed paragraph summarizing the server's purpose and functionality
        - capabilities: List of key features. do not exceed 10 items
        - limitations: 3-5 notable constraints
        Be accurate and direct.
        """

        completion_response:ParsedChatCompletion = await self.client.chat.completions.parse(
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": f"Generate a comprehensive description of the server {server_name} based on the following information."},
                        *[ {"type": "text", "text": item.model_dump_json(indent=2)} for item in enhanced_tools]
                    ]
                }
            ],
            model=self.openai_model_name,
            max_tokens=2048,
            response_format=McpServerDescription
        )

        server_descripton:McpServerDescription = completion_response.choices[0].message.parsed
        return server_descripton
          
   



