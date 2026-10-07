from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..models import User, ApiKey
from ..schemas import RegisterIn, LoginIn
from ..security import *

router=APIRouter(prefix="/auth",tags=["auth"]); bearer=HTTPBearer()
async def current_user(c:HTTPAuthorizationCredentials=Depends(bearer),db:AsyncSession=Depends(get_db)):
    try: uid=int(decode_jwt(c.credentials)["sub"])
    except Exception: raise HTTPException(401,"Invalid token")
    u=await db.get(User,uid)
    if not u: raise HTTPException(401,"User not found")
    return u

@router.post("/register")
async def register(x:RegisterIn,db:AsyncSession=Depends(get_db)):
    if (await db.execute(select(User).where(User.email==x.email))).scalar_one_or_none(): raise HTTPException(409,"Email already registered")
    u=User(email=x.email,password_hash=hash_password(x.password)); db.add(u); await db.commit(); await db.refresh(u)
    return {"token":make_jwt(u.id),"user_id":u.id}

@router.post("/login")
async def login(x:LoginIn,db:AsyncSession=Depends(get_db)):
    u=(await db.execute(select(User).where(User.email==x.email))).scalar_one_or_none()
    if not u or not verify_password(x.password,u.password_hash): raise HTTPException(401,"Invalid credentials")
    return {"token":make_jwt(u.id),"user_id":u.id}

@router.post("/keys")
async def create_key(u=Depends(current_user),db:AsyncSession=Depends(get_db)):
    key=new_api_key(); db.add(ApiKey(user_id=u.id,key_hash=key_hash(key))); await db.commit(); return {"api_key":key}
