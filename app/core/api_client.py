"""
API Client for C# Code Reviewer

This module provides a unified client for interacting with OpenAI (GPT) and Anthropic (Claude) APIs.
It supports streaming responses, error handling, and retry logic.
"""

import os
import time
from typing import Generator, Optional, Dict, Any, Literal
import logging
from dotenv import load_dotenv

# Load environment variables (override system env vars)
load_dotenv(override=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIClientError(Exception):
    """Base exception for API client errors"""
    pass


class APIConnectionError(APIClientError):
    """Raised when connection to API fails"""
    pass


class ModelNotFoundError(APIClientError):
    """Raised when the requested model is not available"""
    pass


class APIKeyMissingError(APIClientError):
    """Raised when API key is not configured"""
    pass


class PromptTooLongError(APIClientError):
    """Raised when prompt exceeds context window"""
    pass


class APIClient:
    """
    Unified client for interacting with OpenAI and Anthropic APIs.

    Attributes:
        provider (str): API provider ('openai' or 'anthropic')
        model_name (str): Name of the LLM model to use
        timeout (int): Request timeout in seconds
        temperature (float): LLM temperature parameter
        max_tokens (int): Maximum tokens to generate
    """

    # Model configurations
    MODELS = {
        'openai': {
            # GPT-5 Series (Latest)
            'gpt-5.1': {'max_tokens': 16384, 'context_window': 128000},
            'gpt-5': {'max_tokens': 16384, 'context_window': 128000},
            'gpt-5-mini': {'max_tokens': 16384, 'context_window': 128000},
            'gpt-5-nano': {'max_tokens': 16384, 'context_window': 128000},
            'gpt-5.1-chat-latest': {'max_tokens': 16384, 'context_window': 128000},
            'gpt-5-chat-latest': {'max_tokens': 16384, 'context_window': 128000},
            'gpt-5.1-codex': {'max_tokens': 16384, 'context_window': 128000},
            'gpt-5-codex': {'max_tokens': 16384, 'context_window': 128000},
            'gpt-5-pro': {'max_tokens': 16384, 'context_window': 128000},
            # GPT-4.1 Series
            'gpt-4.1': {'max_tokens': 16384, 'context_window': 128000},
            'gpt-4.1-mini': {'max_tokens': 16384, 'context_window': 128000},
            'gpt-4.1-nano': {'max_tokens': 16384, 'context_window': 128000},
            # GPT-4 Series
            'gpt-4': {'max_tokens': 8192, 'context_window': 8192},
            'gpt-4-turbo': {'max_tokens': 4096, 'context_window': 128000},
            'gpt-4o': {'max_tokens': 4096, 'context_window': 128000},
            'gpt-4o-2024-05-13': {'max_tokens': 4096, 'context_window': 128000},
            'gpt-4o-mini': {'max_tokens': 16384, 'context_window': 128000},
            # GPT-3.5 Series
            'gpt-3.5-turbo': {'max_tokens': 4096, 'context_window': 16385},
            # Realtime API
            'gpt-realtime': {'max_tokens': 4096, 'context_window': 128000},
        },
        'anthropic': {
            'claude-3-5-sonnet-20241022': {'max_tokens': 8192, 'context_window': 200000},
            'claude-3-5-haiku-20241022': {'max_tokens': 8192, 'context_window': 200000},
            'claude-3-opus-20240229': {'max_tokens': 4096, 'context_window': 200000},
            'claude-3-sonnet-20240229': {'max_tokens': 4096, 'context_window': 200000},
            'claude-3-haiku-20240307': {'max_tokens': 4096, 'context_window': 200000},
        }
    }

    def __init__(
        self,
        provider: Literal['openai', 'anthropic'] = 'openai',
        model_name: Optional[str] = None,
        timeout: int = 60,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ):
        """
        Initialize API client.

        Args:
            provider: API provider ('openai' or 'anthropic')
            model_name: Name of the model to use (default: gpt-4o-mini for OpenAI, claude-3-5-haiku for Anthropic)
            timeout: Request timeout in seconds (default: 60)
            temperature: LLM temperature (default: 0.7)
            max_tokens: Maximum tokens to generate (default: model-specific)
        """
        self.provider = provider
        self.timeout = timeout
        self.temperature = temperature

        # Set default model names
        if model_name is None:
            if provider == 'openai':
                model_name = 'gpt-4o-mini'
            else:  # anthropic
                model_name = 'claude-3-5-haiku-20241022'

        self.model_name = model_name

        # Get model config
        if provider not in self.MODELS or model_name not in self.MODELS[provider]:
            raise ModelNotFoundError(f"Model '{model_name}' not found for provider '{provider}'")

        model_config = self.MODELS[provider][model_name]
        self.context_window = model_config['context_window']
        self.max_tokens = max_tokens or model_config['max_tokens']

        # Initialize API clients
        self._init_clients()

        logger.info(f"Initialized APIClient with provider: {provider}, model: {model_name}")

    def _init_clients(self):
        """Initialize API clients based on provider"""
        if self.provider == 'openai':
            try:
                from openai import OpenAI
                api_key = os.getenv('OPENAI_API_KEY')
                if not api_key:
                    raise APIKeyMissingError("OPENAI_API_KEY not found in environment variables")
                self.client = OpenAI(api_key=api_key, timeout=self.timeout)
                logger.info("OpenAI client initialized")
            except ImportError:
                raise APIClientError("openai package not installed. Run: pip install openai")

        elif self.provider == 'anthropic':
            try:
                from anthropic import Anthropic
                api_key = os.getenv('ANTHROPIC_API_KEY')
                if not api_key:
                    raise APIKeyMissingError("ANTHROPIC_API_KEY not found in environment variables")
                self.client = Anthropic(api_key=api_key, timeout=self.timeout)
                logger.info("Anthropic client initialized")
            except ImportError:
                raise APIClientError("anthropic package not installed. Run: pip install anthropic")

    def test_connection(self) -> bool:
        """
        Test connection to API.

        Returns:
            bool: True if connection successful

        Raises:
            APIConnectionError: If connection fails
            APIKeyMissingError: If API key is missing
        """
        try:
            if self.provider == 'openai':
                # Test with models list
                models = self.client.models.list()
                logger.info(f"Connection successful. Available models: {len(models.data)}")

            elif self.provider == 'anthropic':
                # Test with a minimal message (Anthropic doesn't have a list endpoint)
                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Hi"}]
                )
                logger.info(f"Connection successful. Test response: {response.content[0].text}")

            return True

        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            raise APIConnectionError(f"Failed to connect to {self.provider} API: {e}")

    def analyze_code(
        self,
        prompt: str,
        stream: bool = True,
        max_retries: int = 3
    ) -> Generator[str, None, None] | str:
        """
        Analyze code using LLM.

        Args:
            prompt: The prompt to send to LLM
            stream: Whether to stream the response (default: True)
            max_retries: Maximum number of retry attempts (default: 3)

        Returns:
            Generator yielding response tokens if stream=True, otherwise complete response string

        Raises:
            APIConnectionError: If connection fails after retries
            PromptTooLongError: If prompt exceeds context window
        """
        for attempt in range(max_retries):
            try:
                if stream:
                    return self._stream_response(prompt)
                else:
                    return self._get_response(prompt)

            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {e}")

                if attempt < max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All {max_retries} attempts failed")
                    raise APIConnectionError(f"Failed to get LLM response after {max_retries} attempts: {e}")

    def _stream_response(self, prompt: str) -> Generator[str, None, None]:
        """
        Stream response from LLM.

        Args:
            prompt: The prompt to send

        Yields:
            str: Response tokens
        """
        try:
            logger.info(f"Sending streaming request to {self.provider}/{self.model_name}")
            start_time = time.time()

            if self.provider == 'openai':
                # GPT-5 and GPT-4.1 series use different parameters
                if self.model_name.startswith(('gpt-5', 'gpt-4.1')):
                    # GPT-5 series: use max_completion_tokens, no temperature parameter
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=[{"role": "user", "content": prompt}],
                        max_completion_tokens=self.max_tokens,
                        stream=True
                    )
                else:
                    # GPT-4 and older: use max_tokens and temperature
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=self.temperature,
                        max_tokens=self.max_tokens,
                        stream=True
                    )

                for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content

            elif self.provider == 'anthropic':
                with self.client.messages.stream(
                    model=self.model_name,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=[{"role": "user", "content": prompt}]
                ) as stream:
                    for text in stream.text_stream:
                        yield text

            elapsed = time.time() - start_time
            logger.info(f"Streaming response completed in {elapsed:.2f} seconds")

        except Exception as e:
            logger.error(f"Streaming failed: {e}")
            raise

    def _get_response(self, prompt: str) -> str:
        """
        Get complete response from LLM (non-streaming).

        Args:
            prompt: The prompt to send

        Returns:
            str: Complete response text
        """
        try:
            logger.info(f"Sending non-streaming request to {self.provider}/{self.model_name}")
            start_time = time.time()

            if self.provider == 'openai':
                # GPT-5 and GPT-4.1 series use different parameters
                if self.model_name.startswith(('gpt-5', 'gpt-4.1')):
                    # GPT-5 series: use max_completion_tokens, no temperature parameter
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=[{"role": "user", "content": prompt}],
                        max_completion_tokens=self.max_tokens,
                        stream=False
                    )
                else:
                    # GPT-4 and older: use max_tokens and temperature
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=self.temperature,
                        max_tokens=self.max_tokens,
                        stream=False
                    )
                response_text = response.choices[0].message.content

            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=[{"role": "user", "content": prompt}]
                )
                response_text = response.content[0].text

            elapsed = time.time() - start_time
            logger.info(f"Response received in {elapsed:.2f} seconds ({len(response_text)} chars)")

            return response_text

        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the currently configured model.

        Returns:
            Dict containing model information
        """
        return {
            'provider': self.provider,
            'name': self.model_name,
            'context_window': self.context_window,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature
        }


# Example usage
if __name__ == "__main__":
    import sys

    # Choose provider from command line argument
    provider = sys.argv[1] if len(sys.argv) > 1 else 'openai'

    # Initialize client
    client = APIClient(provider=provider)

    # Test connection
    try:
        client.test_connection()
        print(f"✓ Connection test passed! ({provider})")
    except APIClientError as e:
        print(f"✗ Connection test failed: {e}")
        exit(1)

    # Test simple code review
    test_prompt = """
    당신은 C# 코드 리뷰 전문가입니다. 다음 코드를 분석하고 문제점을 찾아주세요.

    코드:
    ```csharp
    public class Example
    {
        public void ProcessData(string data)
        {
            var result = data.ToUpper();
            Console.WriteLine(result);
        }
    }
    ```

    문제점을 간단히 설명해주세요.
    """

    print("\n" + "="*50)
    print(f"Testing LLM Response (Streaming) - {provider}")
    print("="*50 + "\n")

    try:
        for token in client.analyze_code(test_prompt, stream=True):
            print(token, end='', flush=True)
        print("\n")
    except APIClientError as e:
        print(f"Error: {e}")

    # Get model info
    print("\n" + "="*50)
    print("Model Information:")
    print("="*50)
    model_info = client.get_model_info()
    print(f"Provider: {model_info['provider']}")
    print(f"Model: {model_info['name']}")
    print(f"Context Window: {model_info['context_window']:,} tokens")
    print(f"Max Tokens: {model_info['max_tokens']:,} tokens")
    print(f"Temperature: {model_info['temperature']}")
