from datetime import date
from pydantic import BaseModel, EmailStr
from typing import Optional


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

    class Config:
        from_attributes = True

