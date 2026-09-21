from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os

class Settings(BaseSettings):
    google_cloud_project: str = Field(
        default_factory=lambda: os.getenv("GOOGLE_CLOUD_PROJECT", os.getenv("GCP_PROJECT", "my-project-id")),
        description="Google Cloud Project ID"
    )
    gemini_location: str = Field(default="global", description="Vertex AI / Agent Platform Location for Gemini 3.8 Flash")
    gemini_model: str = Field(default="gemini-3.8-flash", description="Target Gemini Model ID")
    firestore_collection: str = Field(default="user_token_usage", description="Firestore collection for token counting")
    default_thinking_level: str = Field(default="MEDIUM", description="Thinking level: LOW, MEDIUM, or HIGH")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
