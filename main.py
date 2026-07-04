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

@app.patch("/tasks/{task_id}")
def update_task(task_id: int, title: str = None, done: bool = None, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        return {"error": "Task not found"}
    if title is not None:
        task.title = title
    if done is not None:
        task.done = done
    db.commit()
    db.refresh(task)
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        return {"error": "Task not found"}
    db.delete(task)
    db.commit()
    return {"message": f"Task {task_id} deleted"}