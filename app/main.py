from fastapi import FastAPI

app = FastAPI()

# decorater method path


@app.get("/")
async def root():
    return {"message": "Welcome to API"}
