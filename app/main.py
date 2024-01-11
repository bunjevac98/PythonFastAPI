from typing import List
from fastapi import FastAPI, HTTPException, Response, status, Depends
from psycopg2.extras import RealDictCursor
import psycopg2
import time
from sqlalchemy.orm import Session
from . import schemas, utils
from database import models
from database.database import engine, get_db


models.Base.metadata.create_all(bind=engine)


app = FastAPI()


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


"""
@app.get("/")
async def root():
    return {"message": "Welcome to API"}
"""


@app.get("/projects", response_model=List[schemas.ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    projects = db.query(models.Project).all()

    return projects


# Maybe we should add owner_id for now because we dont have user
@app.post(
    "/projects",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.ProjectResponse,
)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    # new_project = models.Project(**project.dict())
    new_project = models.Project(**project.model_dump())

    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


# maybe error with adding new one
@app.get("/projects/{id}/info", response_model=schemas.ProjectResponse)
def get_project(id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"project with id: {id} was now found",
        )

    return project


@app.put("/project/{id}/info", response_model=schemas.ProjectResponse)
def update_project(
    id: int, update_project: schemas.ProjectCreate, db: Session = Depends(get_db)
):
    project_query = db.query(models.Project).filter(models.Project.id == id)
    print(update_project)

    project = project_query.first()
    print(project)
    if project_query is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"passed id:{id} did not exist",
        )

    project_query.update(update_project.model_dump(), synchronize_session=False)

    db.commit()

    return update_project


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


@app.post("/user", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # hash password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.model_dump())

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
