from typing import Optional
from fastapi import FastAPI, HTTPException, Response, status, Depends
from pydantic import BaseModel
from psycopg2.extras import RealDictCursor
import psycopg2
import time
from sqlalchemy.orm import Session
from database import models
from database.database import engine, get_db


models.Base.metadata.create_all(bind=engine)


app = FastAPI()


# If we want to save pdf file it is bytes type in python


class Project(BaseModel):
    name: str
    description: str
    owner_id: int
    logo: str
    # team_members: Optional[list[int]]
    documents: Optional[list[str]]


while True:
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="PythonFastAPI",
            user="postgres",
            password="Ackosi98",
            cursor_factory=RealDictCursor,
        )
        cursor = conn.cursor()
        print("WE CONNECTED")
        break
    except Exception as error:
        print("WE FAILED")
        print("error was:", error)
        time.sleep(3)


my_projects = [
    {
        "id": 1,
        "name": "Project for juniors",
        "description": "This will be nice start for junior",
        "logo": "New Picture",
        "owner": 1,
        "team_members": [1, 2, 3],
        "documents": "some file",
    },
    {
        "id": 2,
        "name": "Project for mediors",
        "description": "This will be nice start for mediors",
        "logo": "Some file",
        "owner": 1,
        "team_members": [2, 4, 5],
        "documents": "Drag some file",
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


"""
@app.get("/")
async def root():
    return {"message": "Welcome to API"}
"""


@app.get("/projects")
def get_projects(db: Session = Depends(get_db)):
    projects = db.query(models.Project).all()

    return {"data": projects}


# Maybe we should add owner_id for now because we dont have user
@app.post("/projects")
def create_project(project: Project, db: Session = Depends(get_db)):
    # new_project = models.Project(**project.dict())
    new_project = models.Project(**project.model_dump())

    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return {"data": new_project}


# maybe error with adding new one
@app.get("/projects/{id}/info")
def get_project(id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"project with id: {id} was now found",
        )

    return {"project_detail": project}


@app.put("/project/{id}/info")
def update_project(id: int, project: Project):
    index = find_index_project(id)
    if index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"passed id:{id} did not exist",
        )
    project_dict = dict(project)
    project_dict["id"] = id
    my_projects[index] = project_dict
    return {"data": project_dict}


# project.dict() is now dict(project) or project.model_dump()
# Proveritiii


@app.delete("/project/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == id)

    if project.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"passed id:{id} did not exist",
        )
    
    project.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
