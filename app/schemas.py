from pydantic import BaseModel
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
#class ProjectUpdate(ProjectBase):

