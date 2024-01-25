from datetime import date
from pydantic import BaseModel, EmailStr
from typing import Optional


class ProjectBase(BaseModel):
    name: str
    description: str
    logo: str


class ProjectCreate(BaseModel):
    name: str
    description: str


# class ProjectUpdate(ProjectBase):
class ProjectResponse(BaseModel):
    name: str
    description: str
    logo: str
    owner_id: int

    class Config:
        from_attributes = True


# ------------USER MODEL-----------------
class UserBase(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    email: EmailStr
    date_of_birth: Optional[date]


class UserCreate(UserBase):
    pass


class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ----------TOKENS FOR LOGIN-------------
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


# ------------DOCUMENTS-----------------
class Document(BaseModel):
    file_name: str
    file_path: str
    project_id: int
    user_id: int


class DocumentRespones(BaseModel):
    file_name: str
    file_path: str


class DocumentUpdate(BaseModel):
    file_name: str


class ProjectInvitationCreate(BaseModel):
    project_id: int
    join_token: str
    email: str
