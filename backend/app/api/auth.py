from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.staff import Staff
from app.schemas.auth import LoginRequest, LoginResponse
from app.core.security import verify_password
from app.core.jwt import create_access_token, create_refresh_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, response: Response, db: Session = Depends(get_db)):
  staff = db.query(Staff).filter(Staff.staff_code == request.staff_code).first()

  if not staff or not staff.is_active:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="担当者IDまたはパスワードが正しくありません"
    )

  if not verify_password(request.password, staff.password_hash):
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="担当者IDまたはパスワードが正しくありません"
    )

  token_data = {"sub": str(staff.staff_id), "role": staff.role}
  access_token = create_access_token(token_data)
  refresh_token = create_refresh_token(token_data)

  # BFF構成: HttpOnly・Secure・SameSite=StrictでCookieに保持
  response.set_cookie(
    key="access_token",
    value=access_token,
    httponly=True,
    secure=True,
    samesite="strict",
    max_age=15 * 60
  )
  response.set_cookie(
    key="refresh_token",
    value=refresh_token,
    httponly=True,
    secure=True,
    samesite="strict",
    max_age=7 * 24 * 60 * 60
  )

  return LoginResponse(
    staff_id=staff.staff_id,
    staff_name=staff.staff_name,
    role=staff.role
  )