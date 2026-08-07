import os
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

logger = logging.getLogger("visionpilot.auth")

CONFIG_PATH = os.path.join("E:\\VisionPilot_AI", "configs", "config.json")
try:
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
except Exception:
    config = {}

auth_config = config.get("auth", {})
SECRET_KEY = os.environ.get("JWT_SECRET") or os.environ.get("SECRET_KEY") or auth_config.get("jwt_secret", "SUPER_SECRET_VISION_PILOT_KEY_12345!")
ALGORITHM = auth_config.get("jwt_algorithm", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = auth_config.get("token_expire_minutes", 1440)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class UserResponse(BaseModel):
    username: str
    role: str

def verify_password(plain_password, hashed_password):
    # For skeleton, if plain matches hashed directly or via bcrypt, allow it.
    # This enables easy mock seeding.
    if plain_password == hashed_password:
        return True
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # Dev/Mock fallback to support Phase 1 frontend local storage token
    if token.startswith("mock_token_"):
        username = token.replace("mock_token_", "")
        role = "admin" if username == "admin" else ("operator" if username == "operator" else "viewer")
        return TokenData(username=username, role=role)

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
        return TokenData(username=username, role=role)
    except JWTError:
        raise credentials_exception

class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: TokenData = Depends(get_current_user)):
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for your user role"
            )
        return current_user
