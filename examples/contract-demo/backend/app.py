import os

from fastapi import FastAPI

DATABASE_URL = os.environ["DATABASE_URL"]
JWT_SECRET = os.environ["JWT_SECRET"]

app = FastAPI()


@app.get("/api/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}


@app.post("/api/users")
def create_user(user: dict):
    return {"ok": True}
