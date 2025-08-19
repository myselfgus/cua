"""
Cloudflare AI Gateway Client

This module provides integration with Cloudflare AI Gateway instead of LiteLLM,
as specified in the project documentation.
"""

import httpx
import os
from typing import Dict, Any, Optional, AsyncGenerator
from pydantic import BaseModel
import json
import asyncio


class CloudflareAIGatewayConfig(BaseModel):
    """Configuration for Cloudflare AI Gateway."""
    account_id: str
    api_token: str
    gateway_url: str = "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1"
    
    @property
    def base_url(self) -> str:
        return self.gateway_url.format(account_id=self.account_id)


class CloudflareAIGateway:
    """Client for Cloudflare AI Gateway integration."""
    
    def __init__(self, config: CloudflareAIGatewayConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {config.api_token}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
    
    async def chat_completion(
        self,
        model: str,
        messages: list,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a chat completion using Cloudflare AI Gateway.
        
        Args:
            model: The model to use (e.g., "openai/gpt-4", "anthropic/claude-3-sonnet")
            messages: List of messages in OpenAI format
            stream: Whether to stream the response
            **kwargs: Additional parameters for the model
        
        Returns:
            Response from the AI model
        """
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            **kwargs
        }
        
        if stream:
            return await self._stream_completion(payload)
        else:
            return await self._completion(payload)
    
    async def _completion(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Non-streaming completion."""
        url = f"{self.config.base_url}/chat/completions"
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"Cloudflare AI Gateway request failed: {e}")
    
    async def _stream_completion(self, payload: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """Streaming completion."""
        url = f"{self.config.base_url}/chat/completions"
        
        try:
            async with self.client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        if data.strip() == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            yield chunk
                        except json.JSONDecodeError:
                            continue
        except httpx.HTTPError as e:
            raise Exception(f"Cloudflare AI Gateway streaming request failed: {e}")
    
    async def embedding(
        self,
        model: str,
        input_text: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create embeddings using Cloudflare AI Gateway.
        
        Args:
            model: The embedding model to use
            input_text: Text to embed
            **kwargs: Additional parameters
        
        Returns:
            Embedding response
        """
        payload = {
            "model": model,
            "input": input_text,
            **kwargs
        }
        
        url = f"{self.config.base_url}/embeddings"
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"Cloudflare AI Gateway embedding request failed: {e}")
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


def create_cloudflare_ai_gateway() -> CloudflareAIGateway:
    """
    Create a Cloudflare AI Gateway client from environment variables.
    
    Returns:
        Configured CloudflareAIGateway instance
    
    Raises:
        ValueError: If required environment variables are missing
    """
    account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    api_token = os.getenv("SECRET_CF_AI_TOKEN")
    gateway_url = os.getenv("APP_AI_GATEWAY_URL")
    
    if not account_id:
        raise ValueError("CLOUDFLARE_ACCOUNT_ID environment variable is required")
    
    if not api_token:
        raise ValueError("SECRET_CF_AI_TOKEN environment variable is required")
    
    if not gateway_url:
        gateway_url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1"
    
    config = CloudflareAIGatewayConfig(
        account_id=account_id,
        api_token=api_token,
        gateway_url=gateway_url
    )
    
    return CloudflareAIGateway(config)


# Example usage
async def example_usage():
    """Example of how to use the Cloudflare AI Gateway."""
    async with create_cloudflare_ai_gateway() as gateway:
        # Chat completion
        response = await gateway.chat_completion(
            model="openai/gpt-4",
            messages=[
                {"role": "user", "content": "Hello, how are you?"}
            ]
        )
        print(response)
        
        # Streaming chat completion
        async for chunk in await gateway.chat_completion(
            model="openai/gpt-4",
            messages=[
                {"role": "user", "content": "Tell me a story"}
            ],
            stream=True
        ):
            print(chunk)
        
        # Embeddings
        embedding_response = await gateway.embedding(
            model="openai/text-embedding-ada-002",
            input_text="This is a test sentence for embedding."
        )
        print(embedding_response)


if __name__ == "__main__":
    asyncio.run(example_usage())