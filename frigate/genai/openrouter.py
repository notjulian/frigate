"""OpenRouter Provider for Frigate AI."""

import base64
import logging
from typing import Optional

from httpx import TimeoutException
from openai import OpenAI

from frigate.config import GenAIProviderEnum
from frigate.genai import GenAIClient, register_genai_provider

logger = logging.getLogger(__name__)


@register_genai_provider(GenAIProviderEnum.openrouter)
class OpenRouterClient(GenAIClient):
    """Generative AI client for Frigate using OpenRouter."""

    provider: OpenAI
    context_size: Optional[int] = None

    def _init_provider(self):
        """Initialize the client."""
        # Set default base_url for OpenRouter if not specified
        base_url = self.genai_config.base_url or "https://openrouter.ai/api/v1"

        return OpenAI(
            api_key=self.genai_config.api_key,
            base_url=base_url,
            **self.genai_config.provider_options
        )

    def _send(self, prompt: str, images: list[bytes]) -> Optional[str]:
        """Submit a request to OpenRouter."""
        encoded_images = [base64.b64encode(image).decode("utf-8") for image in images]
        messages_content = []
        for image in encoded_images:
            messages_content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image}",
                        "detail": "low",
                    },
                }
            )
        messages_content.append(
            {
                "type": "text",
                "text": prompt,
            }
        )
        try:
            result = self.provider.chat.completions.create(
                model=self.genai_config.model,
                messages=[
                    {
                        "role": "user",
                        "content": messages_content,
                    },
                ],
                timeout=self.timeout,
            )
            if (
                result is not None
                and hasattr(result, "choices")
                and len(result.choices) > 0
            ):
                return result.choices[0].message.content.strip()
            return None
        except (TimeoutException, Exception) as e:
            logger.warning("OpenRouter returned an error: %s", str(e))
            return None

    def get_context_size(self) -> int:
        """Get the context window size for OpenRouter models."""
        if self.context_size is not None:
            return self.context_size

        # OpenRouter supports many models with varying context sizes
        # We'll use reasonable defaults based on common model patterns
        model_name = self.genai_config.model.lower()

        # Gemini models via OpenRouter
        if "gemini" in model_name:
            self.context_size = 1000000
        # GPT-4 and GPT-3.5 models
        elif "gpt-4" in model_name or "gpt-3.5" in model_name:
            self.context_size = 128000
        # Claude models
        elif "claude" in model_name:
            if "claude-3-5" in model_name or "claude-3-opus" in model_name:
                self.context_size = 200000
            else:
                self.context_size = 100000
        # Default for other models
        else:
            self.context_size = 8192

        logger.debug(
            f"Using context size {self.context_size} for OpenRouter model {self.genai_config.model}"
        )
        return self.context_size
