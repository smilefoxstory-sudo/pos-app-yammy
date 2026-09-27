import os
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
  return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
  return password_hash.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
  to_encode = data.copy()
  expire = datetime.utcnow() + (expires_delta or timedelta(hours=8))
  to_encode.update({"exp": expire})
  return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_staff(token: str = Depends(oauth2_scheme)) -> dict:
  credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="認証情報が無効です。再度ログインしてください",
    headers={"WWW-Authenticate": "Bearer"},
  )
  expired_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="トークンの有効期限が切れています。再度ログインしてください",
    headers={"WWW-Authenticate": "Bearer"},
  )

  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
  except ExpiredSignatureError:
    raise expired_exception
  except JWTError:
    raise credentials_exception

  staff_code: str = payload.get("sub")
  role: str = payload.get("role")

  if staff_code is None:
    raise credentials_exception

  return {"staff_code": staff_code, "role": role}