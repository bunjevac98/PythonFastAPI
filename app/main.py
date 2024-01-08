from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# If we want to save pdf file it is bytes type in python


class Project(BaseModel):
    id: int
    name: str
    description: str
    owner: int
    team_members: Optional[list]
    attachements: str


my_projects = [
    {
        "id": 1,
        "name": "Project for juniors",
        "description": "This will be nice start for junior",
        "owner": 1,
        "team_members": [1, 2, 3],
        "attachements": "some file",
    },
    {
        "id": 2,
        "name": "Project for mediors",
        "description": "This will be nice start for mediors",
        "owner": 1,
        "team_members": [2, 4, 5],
        "attachements": "Drag some file",
    },
]


def find_project(id):
    for project in my_projects:
        if project["id"] == id:
            return project


@app.get("/")
async def root():
    return {"message": "Welcome to API"}


@app.get("/projects")
def get_projects():
    return {"data": my_projects}


@app.post("/projects")
def create_project(project: Project):
    project_dict = project.model_dump()
    my_projects.append(project_dict)
    print(my_projects)
    return {"data": project_dict}


# maybe error with adding new one
@app.get("/projects/{id}/info")
def get_project(id: int):
    project = find_project(id)
    return {"project_detail": project}
