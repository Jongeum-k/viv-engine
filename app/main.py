from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_db
from app.api.admin_jobs import router as admin_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(admin_router)

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