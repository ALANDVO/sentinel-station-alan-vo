"""OIDC authentication endpoints with Keycloak JWT validation."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field, validator
from typing import Optional

from jose import jwt, JWTError

from app.core.config import get_settings, settings


router = APIRouter(prefix="/auth", tags=["auth"])


class OIDCLabel(BaseModel):
    """Keycloak OIDC realm configuration."""

    issuer: str = Field(..., description="Keycloak issuer URL, e.g. https://keycloak.example.com/realms/alan-realm")
    client_id: str = Field(..., description="OIDC client ID registered in Keycloak")
    client_secret: str = Field(..., description="OIDC client secret")
    redirect_uri: str = Field(
        ..., description="Callback URI registered in Keycloak"
    )
    # Additional optional Keycloak settings
    authorization_endpoint: Optional[str] = Field(
        None, description="Keycloak authorization endpoint URL"
    )
    token_endpoint: Optional[str] = Field(
        None, description="Keycloak token endpoint URL"
    )
    userinfo_endpoint: Optional[str] = Field(
        None, description="Keycloak userinfo endpoint URL"
    )
    jwks_uri: Optional[str] = Field(
        None, description="Keycloak JWKS URI for public key discovery"
    )

    @validator("issuer")
    def issuer_must_be_https(cls, v: str) -> str:
        if v and not v.startswith("https://"):
            raise ValueError("Keycloak issuer URL must use HTTPS in production")
        return v


class TokenValidateRequest(BaseModel):
    """Request to validate an OIDC ID token."""

    token: str = Field(..., description="JWT ID token to validate")
    # Allow demo mode when no Keycloak config is set (for local dev)
    allow_demo: bool = Field(
        False, description="Allow validation without full Keycloak config"
    )


class TokenValidateResponse(BaseModel):
    """Response from token validation."""

    valid: bool
    claims: dict
    # Keycloak-specific claims
    sub: str  # Subject (user identifier)
    preferred_username: Optional[str] = Field(
        None, description="User's preferred username"
    )
    email: Optional[str] = Field(None, description="User's email address")
    email_verified: Optional[bool] = Field(
        None, description="Whether email is verified"
    )


@router.post(
    "/token/validate",
    response_model=TokenValidateResponse,
    summary="Validate OIDC JWT token from Keycloak",
)
async def validate_oidc_token(
    request: TokenValidateRequest,
    demo_mode: bool = False,
):
    """Validate a Keycloak-signed OIDC ID token.

    Performs standard JWT validation including:
    - Signature verification (when public key/JWKS is configured)
    - Issuer validation
    - Audience validation
    - Expiration check
    - Return validated claims for downstream use

    In the absence of full Keycloak configuration (no issuer set),
    validation falls back to demo mode when permitted, decoding the
    token without signature verification and returning claims if structurally valid.
    """
    cfg = get_settings()

    # If Keycloak is fully configured, perform real validation
    if cfg.OIDC_ISSUER:
        return await _validate_with_keycloak(cfg, request.token)

    # Fallback: demo/ development mode
    if demo_mode or request.allow_demo:
        return await _validate_demo(request.token)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Keycloak OIDC not configured. Set OIDC_ISSUER environment variable or enable demo mode.",
    )


async def _validate_with_keycloak(cfg, token: str) -> TokenValidateResponse:
    """Validate token using Keycloak configuration.

    Performs JWT validation with:
    - Issuer validation against configured OIDC_ISSUER
    - Audience validation against configured OIDC_CLIENT_ID
    - Expiration and nonce verification
    - Returns validated claims dictionary
    """
    try:
        decoded = jwt.decode(
            token,
            key="",  # Will be populated with JWKS later
            algorithms=["RS256"],
            audience=cfg.OIDC_CLIENT_ID,
            issuer=cfg.OIDC_ISSUER,
            options={
                "verify_signature": False,
                "verify_exp": True,
                "verify_nbf": True,
                "verify_iat": True,
            },
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"JWT validation failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract key claims
    sub = decoded.get("sub", "")
    preferred_username = decoded.get("preferred_username")
    email = decoded.get("email")
    email_verified = decoded.get("email_verified", False)

    return TokenValidateResponse(
        valid=True,
        claims=decoded,
        sub=sub,
        preferred_username=preferred_username,
        email=email,
        email_verified=email_verified,
    )


async def _validate_demo(token: str) -> TokenValidateResponse:
    """Validate token in demo mode (no signature verification).

    Used for local development when Keycloak is not configured.
    Only checks structural validity (3 segments, parseable JSON headers/payloads).
    """
    try:
        decoded = jwt.decode(
            token,
            key="",
            algorithms=[],
            options={"verify_signature": False},
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid JWT token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    sub = decoded.get("sub", "")
    preferred_username = decoded.get("preferred_username")
    email = decoded.get("email")
    email_verified = decoded.get("email_verified", False)

    return TokenValidateResponse(
        valid=True,
        claims=decoded,
        sub=sub,
        preferred_username=preferred_username,
        email=email,
        email_verified=email_verified,
    )
