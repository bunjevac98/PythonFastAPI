from fastapi import FastAPI
from database import models
from database.database import engine
from .routers import project, user, auth, document

models.Base.metadata.create_all(bind=engine)


app = FastAPI()


app.include_router(project.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(document.router)


@app.get("/")
def root():
    return {"message": "Welcome to API"}
