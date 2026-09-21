import logging
import sys
import json
from datetime import datetime, timezone
from typing import Optional, Literal
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.config import settings
from app.auth import extract_user_identity
from app.gemini_client import gemini_client
from app.database import db

# Configure structured JSON logging for Google Cloud Logging
class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "severity": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if hasattr(record, "json_fields") and isinstance(record.json_fields, dict):
            log_record.update(record.json_fields)
        return json.dumps(log_record)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)

logger = logging.getLogger("proxy_service")

app = FastAPI(
    title="Gemini 3.8 Flash Cloud Run Proxy Service",
    description="Enterprise proxy forwarding IAM-authenticated requests to Gemini 3.8 Flash in Global region with per-user token tracking.",
    version="1.0.0",
)

class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=100000, description="The user query or prompt text")
    thinking_level: Optional[Literal["LOW", "MEDIUM", "HIGH"]] = Field(
        default="MEDIUM",
        description="Thinking level for Gemini 3.8 Flash (LOW, MEDIUM, HIGH). Note: MINIMAL is unsupported.",
    )
    system_instruction: Optional[str] = Field(
        default=None,
        description="Optional system instruction to guide model behavior.",
    )

class TokenUsageResponse(BaseModel):
    prompt_tokens: int
    candidates_tokens: int
    total_tokens: int

class GenerateResponse(BaseModel):
    text: str
    model: str
    user_id: str
    usage: TokenUsageResponse

@app.get("/healthz", tags=["System"])
def healthz():
    """Health check for Cloud Run liveness and readiness probes."""
    return {"status": "ok", "service": "gemini-3.8-flash-proxy"}

@app.post("/v1/generate", response_model=GenerateResponse, tags=["Inference"])
async def generate_content(
    request: GenerateRequest,
    user_id: str = Depends(extract_user_identity),
):
    """
    Forward authenticated request to Gemini 3.8 Flash in global region.
    Tracks and logs per-user input and output tokens.
    """
    try:
        # 1. Forward request to Gemini 3.8 Flash
        gemini_result = gemini_client.generate_content(
            contents=request.prompt,
            thinking_level=request.thinking_level,
            system_instruction=request.system_instruction,
        )

        usage = gemini_result["usage"]
        input_tokens = usage["prompt_tokens"]
        output_tokens = usage["candidates_tokens"]
        total_tokens = usage["total_tokens"]

        # 2. Emit structured log for Cloud Logging / BigQuery Log Export
        logger.info(
            f"Gemini 3.8 Flash generation completed for user '{user_id}'",
            extra={
                "json_fields": {
                    "event_type": "gemini_token_usage",
                    "user_id": user_id,
                    "model": gemini_result["model"],
                    "location": settings.gemini_location,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens,
                    "thinking_level": request.thinking_level,
                }
            },
        )

        # 3. Maintain atomic token count in Firestore
        try:
            db.record_usage(
                user_id=user_id,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model=gemini_result["model"],
            )
        except Exception as db_exc:
            logger.error(f"Failed to persist token usage to database: {db_exc}")
            # Continue responding to user, but log error for alerting

        # 4. Return response to requester
        return GenerateResponse(
            text=gemini_result["text"],
            model=gemini_result["model"],
            user_id=user_id,
            usage=TokenUsageResponse(
                prompt_tokens=input_tokens,
                candidates_tokens=output_tokens,
                total_tokens=total_tokens,
            ),
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Error processing Gemini generation request: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while communicating with Gemini 3.8 Flash.",
        )

@app.get("/v1/users/me/usage", tags=["Analytics"])
async def get_my_usage(user_id: str = Depends(extract_user_identity)):
    """Retrieve cumulative token consumption for the calling user."""
    usage_data = db.get_user_usage(user_id)
    if not usage_data:
        return {
            "user_id": user_id,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_tokens": 0,
            "models": {},
        }
    return usage_data
