import hashlib, secrets
from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext
from .config import settings

pwd=CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p): return pwd.hash(p)
def verify_password(p,h): return pwd.verify(p,h)
def make_jwt(user_id:int):
    exp=datetime.now(timezone.utc)+timedelta(minutes=settings.jwt_expire_minutes)
    return jwt.encode({"sub":str(user_id),"exp":exp}, settings.jwt_secret, algorithm="HS256")
def decode_jwt(token): return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
def new_api_key(): return "sk_"+secrets.token_urlsafe(32)
def key_hash(key): return hashlib.sha256(key.encode()).hexdigest()
