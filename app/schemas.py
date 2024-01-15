from datetime import date
from pydantic import BaseModel, EmailStr
from typing import ClassVar, Optional


class ProjectBase(BaseModel):
    name: str
    description: str
    owner_id: int
    logo: str
    # team_members: Optional[list[int]]
    documents: Optional[list[str]]


class ProjectCreate(ProjectBase):
    pass


#
# class ProjectUpdate(ProjectBase):
# probably team_members we sand too
class ProjectResponse(BaseModel):
    name: str
    description: str
    logo: str
    documents: Optional[list[str]]

    class Config:
        from_attributes = True


# ------------USER MODEL-----------------
class UserBase(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    email: EmailStr
    picture: Optional[str]
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


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None
