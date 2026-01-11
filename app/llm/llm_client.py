"""
LLM client with support for both Google Gemini (local) and Azure OpenAI (production).
"""

import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
import google.generativeai as genai
from openai import AsyncAzureOpenAI
import tiktoken
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Unified LLM client supporting Google Gemini and Azure OpenAI."""
    
    def __init__(self):
        """Initialize LLM client based on environment."""
        self.environment = settings.environment
        self.client = None
        self.embedding_client = None
        
        if settings.use_gemini:
            logger.info("Initializing Google Gemini client for local environment")
            genai.configure(api_key=settings.google_gemini_api_key)
            self.model = genai.GenerativeModel(settings.google_gemini_model)
            self.embedding_model = settings.google_gemini_embedding_model
            self.provider = "gemini"
        elif settings.use_azure:
            logger.info("Initializing Azure OpenAI client for production environment")
            self.client = AsyncAzureOpenAI(
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version,
                azure_endpoint=settings.azure_openai_endpoint
            )
            self.model = settings.azure_openai_deployment_name
            self.embedding_model = settings.azure_openai_embedding_deployment
            self.provider = "azure"
        else:
            raise ValueError("No valid LLM configuration found. Check environment variables.")
        
        # Token encoder (works for both)
        try:
            self.encoder = tiktoken.get_encoding("cl100k_base")
        except Exception:
            self.encoder = None
            logger.warning("Could not load tiktoken encoder")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        if self.encoder:
            return len(self.encoder.encode(text))
        # Rough estimate if encoder not available
        return int(len(text.split()) * 1.3)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate completion from LLM.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            Generated text
        """
        temperature = temperature or settings.temperature
        max_tokens = max_tokens or settings.max_tokens
        
        try:
            if self.provider == "gemini":
                # Combine system and user prompts for Gemini
                full_prompt = prompt
                if system_prompt:
                    full_prompt = f"{system_prompt}\n\n{prompt}"
                
                # Configure generation
                generation_config = genai.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    top_p=settings.top_p,
                )
                
                # Generate
                response = await asyncio.to_thread(
                    self.model.generate_content,
                    full_prompt,
                    generation_config=generation_config
                )
                
                try:
                    # Method 1: Check candidates and parts (Most robust)
                    if response.candidates:
                        candidate = response.candidates[0]
                        if candidate.content and candidate.content.parts:
                            text = "".join([part.text for part in candidate.content.parts])
                            if text.strip():
                                return text.strip()
                    
                    # Method 2: Try accessing text property safely
                    try:
                        if response.text:
                            return response.text.strip()
                    except ValueError:
                        # expected for multi-part responses
                        pass
                        
                    # Method 3: Check prompt feedback if blocked
                    if response.prompt_feedback:
                        logger.warning(f"Gemini prompt feedback: {response.prompt_feedback}")
                        
                    return ""
                except Exception as e:
                    logger.error(f"Error parsing Gemini response: {e}")
                    # Don't raise, just return empty string to allow fallback logic in caller
                    return ""
            
            else:  # Azure OpenAI
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=settings.top_p,
                    **kwargs
                )
                
                return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"Error generating completion: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def generate_with_history(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate completion with conversation history.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            Generated text
        """
        temperature = temperature or settings.temperature
        max_tokens = max_tokens or settings.max_tokens
        
        try:
            if self.provider == "gemini":
                # Convert messages to Gemini format
                # Gemini uses a simpler format, combine into single prompt
                conversation = []
                for msg in messages:
                    role = "User" if msg["role"] == "user" else "Assistant"
                    conversation.append(f"{role}: {msg['content']}")
                
                full_prompt = "\n\n".join(conversation)
                
                generation_config = genai.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    top_p=settings.top_p,
                )
                
                response = await asyncio.to_thread(
                    self.model.generate_content,
                    full_prompt,
                    generation_config=generation_config
                )
                
                try:
                    # Method 1: Check candidates and parts
                    if response.candidates:
                        candidate = response.candidates[0]
                        if candidate.content and candidate.content.parts:
                            text = "".join([part.text for part in candidate.content.parts])
                            if text.strip():
                                return text.strip()
                                
                    # Method 2: Try accessing text property safely
                    try:
                        if response.text:
                            return response.text.strip()
                    except ValueError:
                        pass

                    return ""
                except Exception as e:
                    logger.error(f"Error parsing Gemini response history: {e}")
                    return ""
            
            else:  # Azure OpenAI
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=settings.top_p,
                    **kwargs
                )
                
                return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"Error generating with history: {e}")
            raise
    
    async def stream_generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Stream completion from LLM.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Yields:
            Text chunks
        """
        temperature = temperature or settings.temperature
        max_tokens = max_tokens or settings.max_tokens
        
        try:
            if self.provider == "gemini":
                # Gemini streaming (basic implementation)
                full_prompt = prompt
                if system_prompt:
                    full_prompt = f"{system_prompt}\n\n{prompt}"
                
                generation_config = genai.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
                
                response = await asyncio.to_thread(
                    self.model.generate_content,
                    full_prompt,
                    generation_config=generation_config,
                    stream=True
                )
                
                for chunk in response:
                    if chunk.text:
                        yield chunk.text
            
            else:  # Azure OpenAI
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                stream = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=settings.top_p,
                    stream=True,
                    **kwargs
                )
                
                async for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
        
        except Exception as e:
            logger.error(f"Error streaming completion: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        try:
            if self.provider == "gemini":
                # Use Gemini embedding model
                result = await asyncio.to_thread(
                    genai.embed_content,
                    model=self.embedding_model,
                    content=text,
                    task_type="retrieval_document"
                )
                return result['embedding']
            
            else:  # Azure OpenAI
                # Small delay to avoid rate limits on standard/free tiers
                await asyncio.sleep(5)
                response = await self.client.embeddings.create(
                    model=self.embedding_model,
                    input=text
                )
                return response.data[0].embedding
        
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    async def generate_embeddings_batch(
        self,
        texts: List[str],
        batch_size: int = 16
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.
        
        Args:
            texts: List of input texts
            batch_size: Batch size for processing
            
        Returns:
            List of embedding vectors
        """
        all_embeddings = []
        
        # Gemini has different batch handling
        if self.provider == "gemini":
            # Process one by one for Gemini (API limitation)
            for text in texts:
                embedding = await self.generate_embedding(text)
                all_embeddings.append(embedding)
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.1)
        else:
            # Azure OpenAI supports native batching (one API call per batch)
            # This is much more efficient and avoids rate limits
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                try:
                    response = await self.client.embeddings.create(
                        model=self.embedding_model,
                        input=batch
                    )
                    # Extract embeddings in order
                    # response.data is sorted by index
                    batch_embeddings = [item.embedding for item in response.data]
                    all_embeddings.extend(batch_embeddings)
                    
                    # Small delay between batches
                    await asyncio.sleep(0.2)
                except Exception as e:
                    logger.error(f"Error generating batch embeddings: {e}")
                    # Fallback to individual processing if batch fails
                    logger.info("Falling back to individual processing for batch")
                    fallback_embeddings = await asyncio.gather(
                        *[self.generate_embedding(text) for text in batch]
                    )
                    all_embeddings.extend(fallback_embeddings)
        
        return all_embeddings


# Global LLM client instance
llm_client = LLMClient()
