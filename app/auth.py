import logging
import secrets

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.models import LoginData

logger = logging.getLogger(__name__)

USERNAME = "aarav"
PASSWORD = "akshu"
valid_tokens: set[str] = set()
security = HTTPBearer(auto_error=False)


def require_login(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
):
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "UNAUTHORIZED",
                "message": "Login required. Please authorize first.",
            },
        )

    token = credentials.credentials
    if token not in valid_tokens:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "UNAUTHORIZED",
                "message": "Invalid or expired token",
            },
        )

    return token


def login_user(data: LoginData) -> dict:
    if data.username != USERNAME or data.password != PASSWORD:
        logger.warning("Login failed")
        raise HTTPException(
            status_code=401,
            detail={"error": "UNAUTHORIZED", "message": "Invalid username or password"},
        )

    token = secrets.token_hex(16)
    valid_tokens.add(token)
    logger.info("Login successful")
    return {"access_token": token, "token_type": "bearer"}
