from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
import models
import auth

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
def get_tasks(db: Session = Depends(get_db), current_user: str = Depends(auth.get_current_user_email)):
    return db.query(models.Task).all()

@app.post("/tasks")
def add_task(title: str, db: Session = Depends(get_db), current_user: str = Depends(auth.get_current_user_email)):
    new_task = models.Task(title=title, done=False)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.patch("/tasks/{task_id}")
def update_task(task_id: int, title: str = None, done: bool = None, db: Session = Depends(get_db), current_user: str = Depends(auth.get_current_user_email)):
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
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: str = Depends(auth.get_current_user_email)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        return {"error": "Task not found"}
    db.delete(task)
    db.commit()
    return {"message": f"Task {task_id} deleted"}

@app.post("/signup")
def signup(email: str, password: str, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == email).first()
    if existing_user:
        return {"error": "Email already registered"}
    hashed_pw = auth.hash_password(password)
    new_user = models.User(email=email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully", "user_id": new_user.id}

@app.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        return {"error": "Invalid email or password"}
    token = auth.create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}