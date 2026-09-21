import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from google.cloud import firestore
from app.config import settings

logger = logging.getLogger("proxy_service.database")

class TokenDatabase:
    """Manages per-user token usage persistence using Cloud Firestore with atomic increments."""

    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id or settings.google_cloud_project
        self._client: Optional[firestore.Client] = None

    @property
    def client(self) -> firestore.Client:
        if self._client is None:
            self._client = firestore.Client(project=self.project_id)
        return self._client

    def record_usage(
        self,
        user_id: str,
        input_tokens: int,
        output_tokens: int,
        model: str = settings.gemini_model,
    ) -> Dict[str, Any]:
        """
        Atomically records input, output, and total token usage for a user.
        Uses Firestore atomic increment (`firestore.Increment`) to prevent race conditions.
        """
        total_tokens = input_tokens + output_tokens
        doc_ref = self.client.collection(settings.firestore_collection).document(user_id)

        update_payload = {
            "user_id": user_id,
            "total_input_tokens": firestore.Increment(input_tokens),
            "total_output_tokens": firestore.Increment(output_tokens),
            "total_tokens": firestore.Increment(total_tokens),
            "last_active": firestore.SERVER_TIMESTAMP,
            f"models.{model.replace('.', '_')}.input_tokens": firestore.Increment(input_tokens),
            f"models.{model.replace('.', '_')}.output_tokens": firestore.Increment(output_tokens),
            f"models.{model.replace('.', '_')}.total_tokens": firestore.Increment(total_tokens),
        }

        # Atomically update or create document
        doc_ref.set(update_payload, merge=True)

        logger.info(
            f"Recorded usage for user '{user_id}': +{input_tokens} input, +{output_tokens} output, +{total_tokens} total"
        )
        return {
            "user_id": user_id,
            "recorded_input_tokens": input_tokens,
            "recorded_output_tokens": output_tokens,
            "recorded_total_tokens": total_tokens,
        }

    def get_user_usage(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves current token usage statistics for a given user."""
        doc_ref = self.client.collection(settings.firestore_collection).document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None

db = TokenDatabase()
