from fastapi import FastAPI
from psycopg2.extras import RealDictCursor
import psycopg2
import time
from database import models
from database.database import engine
from .routers import project, user, auth

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


app.include_router(project.router)
app.include_router(user.router)
app.include_router(auth.router)


@app.get("/")
def root():
    return {"message": "Welcome to API"}
