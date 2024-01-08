from typing import Optional
from fastapi import FastAPI, HTTPException, Response, status
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


def find_index_project(id):
    for i, p in enumerate(my_projects):
        if p["id"] == id:
            return i


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
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"project with id: {id} was now found",
        )

    return {"project_detail": project}


@app.delete("/project/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(id: int):
    index = find_index_project(id)
    if index == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"passed id:{id} did not exist",
        )

    my_projects.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
