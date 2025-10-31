# app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app import schema
from app.models.user import User
from app.core.security import get_password_hash, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register")
def register(body: schema.RegisterIn, db: Session = Depends(get_db)):
    # check existence
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=400, detail="Username đã tồn tại")
    if body.email and db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email đã được đăng ký")

    hashed = get_password_hash(body.password)
    user = User(username=body.username, email=body.email, hashed_password=hashed, role="user")
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"msg": "register_success"}

@router.post("/login", response_model=schema.TokenOut)
def login(body: schema.LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Sai username hoặc password")
    token = create_access_token(subject=user.username, role=user.role)
    return {"access_token": token, "token_type": "bearer", "role": user.role, "username": user.username}
