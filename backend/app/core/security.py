# app/core/security.py
import os
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.core.config import settings  # Lấy SECRET_KEY, ALGORITHM, EXPIRE_MINUTES từ config.py

# ================== Cấu hình ==================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# ================== Mã hóa mật khẩu ==================
def get_password_hash(password: str) -> str:
    """Tạo hash từ mật khẩu gốc"""
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    """Xác thực mật khẩu"""
    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        return False

# ================== JWT Token ==================
def create_access_token(subject: str, role: str, expires_delta: Optional[timedelta] = None) -> str:
    """Tạo JWT access token"""
    to_encode = {"sub": subject, "role": role}
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# ================== Xác thực người dùng ==================
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Giải mã JWT và truy vấn người dùng hiện tại"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực người dùng.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise credentials_exception

    return user

# ================== Chỉ cho phép admin ==================
def get_current_admin_user(current_user: User = Depends(get_current_user)):
    """Chỉ cho phép người dùng có role=admin"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập tài nguyên này.",
        )
    return current_user
