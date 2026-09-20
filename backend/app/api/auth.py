from fastapi import APIRouter,HTTPException
from pydantic import BaseModel,Field
from app.core.security import hash_password,verify_password,token
router=APIRouter(prefix="/auth",tags=["Auth"])
users={}
class User(BaseModel):
    username:str=Field(min_length=3)
    password:str=Field(min_length=6)
    role:str="viewer"
class Login(BaseModel):
    username:str
    password:str
@router.post("/register")
def register(x:User):
    if x.username in users: raise HTTPException(409,"User exists")
    if x.role not in ("admin","devops","viewer"): raise HTTPException(400,"Invalid role")
    users[x.username]={"password":hash_password(x.password),"role":x.role}
    return {"message":"registered"}
@router.post("/login")
def login(x:Login):
    u=users.get(x.username)
    if not u or not verify_password(x.password,u["password"]): raise HTTPException(401,"Invalid credentials")
    return {"access_token":token(x.username,u["role"]),"token_type":"bearer","role":u["role"]}
