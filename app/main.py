from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_db

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def read_root():
    return {"message": "Howdy, cowboy. FastAPI is up and runnin"}

@app.get("/health/db")
def check_db(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1 AS ok"))
    row = result.fetchone()

    return {
        "status": "ok",
        "database": "connected",
        "data": row.ok,
    }