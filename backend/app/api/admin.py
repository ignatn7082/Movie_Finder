from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.schema import UserResponse # tạo schema bên dưới
from app.core.security import get_current_admin_user
from pydantic import BaseModel


router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.get("/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db), current_user=Depends(get_current_admin_user)):
    users = db.query(User).all()
    return users


class RoleUpdate(BaseModel):
    role: str

@router.put("/users/{user_id}/role")
def update_user_role(user_id: int, body: RoleUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_admin_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = body.role
    db.commit()
    return {"message": "Role updated"}



@router.put("/users/{user_id}/active")
def toggle_active(user_id: int, body: dict, db: Session = Depends(get_db), current_user=Depends(get_current_admin_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Không có quyền")
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy user")

    user.is_active = body.get("is_active", True)
    db.commit()
    return {"msg": f"Tài khoản {user.username} đã {'kích hoạt' if user.is_active else 'vô hiệu hóa'}"}


