from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.database import engine, get_db
import threading
from app.telegram_bot import run_bot

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="TaskTracker API")

@app.on_event("startup")
def start_bot():
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()

@app.get("/")
def root():
    return {"message": "TaskTracker API running"}

@app.post("/habits/", response_model=schemas.HabitResponse)
def create_habit(habit: schemas.HabitCreate, db: Session = Depends(get_db)):
    return crud.create_habit(db, habit)

@app.get("/habits/", response_model=list[schemas.HabitResponse])
def read_habits(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_habits(db, skip=skip, limit=limit)

@app.delete("/habits/{habit_id}")
def delete_habit(habit_id: int, db: Session = Depends(get_db)):
    if crud.delete_habit(db, habit_id):
        return {"ok": True}
    raise HTTPException(status_code=404, detail="Habit not found")

@app.post("/habits/{habit_id}/log")
def log_habit_today(habit_id: int, db: Session = Depends(get_db)):
    from datetime import date
    crud.log_habit(db, habit_id, date.today(), True)
    return {"ok": True}