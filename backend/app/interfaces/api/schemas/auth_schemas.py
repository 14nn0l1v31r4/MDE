from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Senha com no mínimo 8 caracteres")
    full_name: str = Field(..., min_length=2, description="Nome completo do usuário")
    role: str = Field(default="analyst", description="Papel do usuário (analyst, admin, viewer)")


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime | None = None

