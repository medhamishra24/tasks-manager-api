from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
import models

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"message": "hello, FastAPI!"}

@app.get("/tasks")
def get_tasks(db: Session = Depends(get_db)):
    return db.query(models.Task).all()

@app.post("/tasks")
def add_task(title: str, db: Session = Depends(get_db)):
    new_task = models.Task(title=title, done=False)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task