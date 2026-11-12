from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token, generate_csrf_token
from app.core.rate_limit import rate_limiter
from app.models.user import User, UserRole
from app.models.audit import AuditLog
from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(req: UserRegister, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    rate_limiter.check_rate_limit(f"register_{client_ip}", max_requests=10, window_seconds=60)

    # Check if user already exists
    existing = db.query(User).filter(User.email == req.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )

    # Public registration strictly creates STUDENT role only
    user = User(
        email=req.email.lower(),
        hashed_password=get_password_hash(req.password),
        full_name=req.full_name,
        role=UserRole.STUDENT,
        student_index=req.student_index,
        faculty=req.faculty or "Faculty of Computing",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    db.add(AuditLog(
        user_id=user.id,
        action="USER_REGISTER",
        resource_type="USER",
        resource_id=str(user.id),
        details=f"Student account created: {user.email}",
        ip_address=client_ip
    ))
    db.commit()

    return user

@router.post("/login", response_model=TokenResponse)
def login(req: UserLogin, request: Request, response: Response, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    rate_limiter.check_rate_limit(f"login_{client_ip}", max_requests=settings.LOGIN_RATE_LIMIT_PER_MINUTE, window_seconds=60)

    user = db.query(User).filter(User.email == req.email.lower()).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated. Contact administration."
        )

    token = create_access_token(subject=user.id)
    csrf_token = generate_csrf_token()

    # Set secure HttpOnly cookie
    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    # Set CSRF cookie readable by JS for header inclusion
    response.set_cookie(
        key=settings.CSRF_COOKIE_NAME,
        value=csrf_token,
        httponly=False,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )

    db.add(AuditLog(
        user_id=user.id,
        action="USER_LOGIN",
        resource_type="USER",
        resource_id=str(user.id),
        details=f"Login successful for role {user.role.value}",
        ip_address=client_ip
    ))
    db.commit()

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=user
    )

@router.post("/logout")
def logout(response: Response, current_user: User = Depends(get_current_user)):
    response.delete_cookie(key=settings.COOKIE_NAME, path="/")
    response.delete_cookie(key=settings.CSRF_COOKIE_NAME, path="/")
    return {"message": "Successfully logged out."}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
