from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str


class UserOut(BaseModel):
    id: UUID
    email: Optional[str]
    name: str
    is_active: bool
    is_seller: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserMe(BaseModel):
    id: UUID
    email: Optional[str]
    name: str
    vk_linked: bool

    class Config:
        from_attributes = False


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class VkTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    is_new_user: bool
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterResponse(BaseModel):
    message: str = "ok"


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    message: str = "if email exists, link sent"


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class ResetPasswordResponse(BaseModel):
    message: str = "password updated"


class RefreshRequest(BaseModel):
    refresh_token: str


class VkAuthRequest(BaseModel):
    code: str
    redirect_uri: str


class LinkVkRequest(BaseModel):
    code: str
    redirect_uri: str


class LinkVkResponse(BaseModel):
    vk_linked: bool = True