from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import Staff
from security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
  staff_code: str
  password: str


class LoginResponse(BaseModel):
  access_token: str
  token_type: str = "bearer"


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
  staff = db.query(Staff).filter(Staff.staff_code == request.staff_code).first()

  if not staff or not verify_password(request.password, staff.password_hash):
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="staff_codeまたはpasswordが正しくありません",
    )

  access_token = create_access_token(
    data={"sub": staff.staff_code, "role": staff.role},
    expires_delta=timedelta(hours=8),
  )

  return LoginResponse(access_token=access_token)