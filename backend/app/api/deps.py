from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.core.security import decode_access_token
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)

def get_token_from_request(request: Request, bearer_token: Optional[str] = Depends(oauth2_scheme)) -> Optional[str]:
    # 1. Explicit Bearer Authorization header takes precedence
    if bearer_token:
        return bearer_token
    # 2. Fall back to HttpOnly cookie
    cookie_token = request.cookies.get(settings.COOKIE_NAME)
    if cookie_token:
        return cookie_token
    return None

def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(get_token_from_request)
) -> User:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = int(payload["sub"])
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account inactive or not found",
        )

    return user

def require_role(*allowed_roles: UserRole):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted for role '{current_user.role.value}'. Requires: {[r.value for r in allowed_roles]}",
            )
        return current_user
    return role_checker

require_student = require_role(UserRole.STUDENT, UserRole.STAFF, UserRole.ADMIN)
require_staff = require_role(UserRole.STAFF, UserRole.ADMIN)
require_admin = require_role(UserRole.ADMIN)

def verify_csrf(request: Request):
    """Verify CSRF token for state-mutating requests when using cookie-based auth."""
    if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
        cookie_token = request.cookies.get(settings.COOKIE_NAME)
        if cookie_token:
            csrf_cookie = request.cookies.get(settings.CSRF_COOKIE_NAME)
            csrf_header = request.headers.get("X-CSRF-Token")
            # If CSRF cookie is present, match header
            if csrf_cookie and csrf_header and csrf_cookie != csrf_header:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF token validation failed.")
