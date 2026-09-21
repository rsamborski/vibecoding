import logging
from typing import Optional, Dict, Any
from fastapi import Header, HTTPException, status
from google.oauth2 import id_token
from google.auth.transport import requests
import jwt

logger = logging.getLogger("proxy_service.auth")

def extract_user_identity(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_goog_authenticated_user_email: Optional[str] = Header(None, alias="X-Goog-Authenticated-User-Email"),
) -> str:
    """
    Extracts and identifies the authenticated caller's identity (email or unique subject ID).

    Cloud Run enforces IAM authentication at the infrastructure layer (GFE) before traffic
    reaches this container when `--no-allow-unauthenticated` is configured.
    Callers must supply a valid Google OIDC ID token: `Authorization: Bearer <ID_TOKEN>`.

    This function reads:
    1. `X-Goog-Authenticated-User-Email` (injected if behind Identity-Aware Proxy or Cloud Load Balancer)
    2. Decoded claims (`email` or `sub`) from the Google-signed OIDC ID Token in `Authorization: Bearer ...`
    """
    # 1. Check IAP header if present
    if x_goog_authenticated_user_email:
        # Format is typically "accounts.google.com:user@example.com"
        clean_email = x_goog_authenticated_user_email.split(":")[-1]
        if clean_email:
            return clean_email

    # 2. Check Authorization header
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header. An authenticated Google OIDC ID token is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Expected 'Bearer <ID_TOKEN>'.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    raw_token = parts[1]

    try:
        # Note: Cloud Run already validated signature & audience at the Google Front End (GFE).
        # We decode the payload to extract caller claims (email/sub) for token attribution.
        # unverified headers/claims decode for user attribution:
        unverified_claims: Dict[str, Any] = jwt.decode(
            raw_token,
            options={"verify_signature": False, "verify_aud": False, "verify_exp": False},
        )

        user_email = unverified_claims.get("email")
        if user_email:
            return user_email

        user_sub = unverified_claims.get("sub")
        if user_sub:
            return f"account-{user_sub}"

        return "unknown_authenticated_user"

    except Exception as exc:
        logger.error(f"Failed to parse caller token: {exc}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token payload.",
            headers={"WWW-Authenticate": "Bearer"},
        )
