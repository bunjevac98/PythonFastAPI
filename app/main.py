from fastapi import FastAPI


app = FastAPI()
#decorater method path
@app.get("/")
#function
async def root():
    return {"message": "Welcome to API"}


