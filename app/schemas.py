from datetime import date
from pydantic import BaseModel, EmailStr
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


#
# class ProjectUpdate(ProjectBase):
# probably team_members we sand too
class ProjectResponse(BaseModel):
    name: str
    description: str
    logo: str
    # documents: Optional[list[str]]
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
    # picture: Optional[str]
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


class Document(BaseModel):
    file_name: str
    file_path: str
    project_id: int
    user_id: int


class AllowedExtensions:
    pdf: {"pdf"}
    docx: {"docx"}
