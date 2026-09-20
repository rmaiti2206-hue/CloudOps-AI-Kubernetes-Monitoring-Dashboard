from datetime import datetime,timedelta,timezone
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings
pwd=CryptContext(schemes=["bcrypt"],deprecated="auto")

def hash_password(x): return pwd.hash(x)
def verify_password(x,y): return pwd.verify(x,y)
def token(username,role):
    exp=datetime.now(timezone.utc)+timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({"sub":username,"role":role,"exp":exp},settings.jwt_secret,algorithm=settings.jwt_algorithm)
