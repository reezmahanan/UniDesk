from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.department import Department
from app.schemas.user import UserResponse
from app.api.deps import require_admin, get_current_user

router = APIRouter(prefix="/users", tags=["Users & Departments"])

class UserRoleUpdate(BaseModel):
    role: UserRole
    department_id: Optional[int] = None
    is_active: Optional[bool] = None

class DepartmentResponse(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str] = None
    email: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

@router.get("", response_model=List[UserResponse])
def list_users(
    role: Optional[UserRole] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    return query.order_by(User.created_at.desc()).all()

@router.patch("/{user_id}", response_model=UserResponse)
def update_user_role_and_dept(
    user_id: int,
    req: UserRoleUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    user.role = req.role
    if req.department_id is not None:
        user.department_id = req.department_id
    if req.is_active is not None:
        user.is_active = req.is_active

    db.commit()
    db.refresh(user)
    return user

@router.get("/departments", response_model=List[DepartmentResponse])
def list_departments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Department).filter(Department.is_active == True).all()
