from datetime import date
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class ProjectBase(BaseModel):
    name: str
    description: str
    logo: str
    # documents: Optional[list[str]]
    # team_members: Optional[list[int]]
    # owner_id: int


class ProjectCreate(ProjectBase):
    pass


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


class DocumentUpdate(BaseModel):
    file_name: str = Field(None, title="Updated File Name", max_length=255)
