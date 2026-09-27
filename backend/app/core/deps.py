# app/core/deps.py
from fastapi import Depends, HTTPException, Request, status
import jwt
from jwt import PyJWTError

from app.core.config import settings

def get_current_staff(request: Request):
  token = request.cookies.get("access_token")
  if not token:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未ログインです")

  try:
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    return {"staff_id": payload.get("sub"), "role": payload.get("role")}
  except PyJWTError:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="トークンが無効です")

def require_admin(current_staff: dict = Depends(get_current_staff)):
  if current_staff["role"] != "admin":
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="権限がありません")
  return current_staff