import logging
from typing import Dict, Any, Optional
from google import genai
from google.genai import types
from app.config import settings

logger = logging.getLogger("proxy_service.gemini")

class GeminiProxyClient:
    """Client for forwarding requests to Gemini 3.8 Flash on Gemini Enterprise Agent Platform."""

    def __init__(
        self,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        model_id: Optional[str] = None,
    ):
        self.project_id = project_id or settings.google_cloud_project
        self.location = location or settings.gemini_location
        self.model_id = model_id or settings.gemini_model
        self._client: Optional[genai.Client] = None

    @property
    def client(self) -> genai.Client:
        if self._client is None:
            # Initialize with enterprise=True and location="global"
            self._client = genai.Client(
                enterprise=True,
                project=self.project_id,
                location=self.location,
            )
        return self._client

    def generate_content(
        self,
        contents: Any,
        thinking_level: Optional[str] = None,
        system_instruction: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Invokes Gemini 3.8 Flash adhering to Gemini 3 family API conventions:
        - Uses `thinking_level` (LOW, MEDIUM, HIGH) instead of legacy budget
        - Omits deprecated/unsupported sampling parameters (temperature, top_p, top_k)
        """
        level = (thinking_level or settings.default_thinking_level).upper()
        if level not in ["LOW", "MEDIUM", "HIGH"]:
            level = "MEDIUM"

        config_kwargs: Dict[str, Any] = {
            "thinking_config": types.ThinkingConfig(thinking_level=level)
        }

        if system_instruction:
            config_kwargs["system_instruction"] = system_instruction

        config = types.GenerateContentConfig(**config_kwargs)

        logger.info(
            f"Forwarding request to model='{self.model_id}', location='{self.location}', thinking_level='{level}'"
        )

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=contents,
            config=config,
        )

        # Extract usage metadata
        usage = getattr(response, "usage_metadata", None)
        prompt_tokens = getattr(usage, "prompt_token_count", 0) if usage else 0
        candidates_tokens = getattr(usage, "candidates_token_count", 0) if usage else 0
        total_tokens = getattr(usage, "total_token_count", prompt_tokens + candidates_tokens) if usage else prompt_tokens + candidates_tokens

        return {
            "text": response.text if response.text is not None else "",
            "usage": {
                "prompt_tokens": prompt_tokens,
                "candidates_tokens": candidates_tokens,
                "total_tokens": total_tokens,
            },
            "model": self.model_id,
        }

gemini_client = GeminiProxyClient()
