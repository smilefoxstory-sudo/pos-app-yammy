from pydantic import BaseModel

class LoginRequest(BaseModel):
  staff_code: str
  password: str

class LoginResponse(BaseModel):
  staff_id: int
  staff_name: str
  role: str