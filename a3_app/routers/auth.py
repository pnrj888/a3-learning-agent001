# 认证路由
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

from database import get_db
from models.db_models import User, UserProfile
from schemas.pydantic_models import LoginRequest, RegisterRequest, TokenResponse
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/api/auth", tags=["认证"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_token(user_id: int, username: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(user_id), "name": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register")
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.username == req.username))
    if existing.scalar_one_or_none():
        raise HTTPException(400, "用户名已存在")
    user = User(username=req.username, hashed_password=pwd_context.hash(req.password), display_name=req.display_name)
    db.add(user)
    await db.flush()
    profile = UserProfile(user_id=user.id)
    db.add(profile)
    await db.commit()
    return TokenResponse(access_token=create_token(user.id, user.username), user_id=user.id, display_name=user.display_name)

@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == req.username))
    user = result.scalar_one_or_none()
    if not user or not pwd_context.verify(req.password, user.hashed_password):
        raise HTTPException(401, "用户名或密码错误")
    return TokenResponse(access_token=create_token(user.id, user.username), user_id=user.id, display_name=user.display_name)
