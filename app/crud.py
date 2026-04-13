from sqlalchemy.orm import Session
from app import models, schemas
from datetime import date

def get_habit(db: Session, habit_id: int):
    return db.query(models.Habit).filter(models.Habit.id == habit_id).first()

def get_habits(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Habit).filter(models.Habit.active == True).offset(skip).limit(limit).all()

def create_habit(db: Session, habit: schemas.HabitCreate):
    db_habit = models.Habit(name=habit.name, frequency=habit.frequency)
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    return db_habit

def delete_habit(db: Session, habit_id: int):
    db_habit = get_habit(db, habit_id)
    if db_habit:
        db_habit.active = False
        db.commit()
        return True
    return False

def log_habit(db: Session, habit_id: int, log_date: date, done: bool):
    existing = db.query(models.HabitLog).filter(
        models.HabitLog.habit_id == habit_id,
        models.HabitLog.date == log_date
    ).first()
    if existing:
        existing.done = done
    else:
        new_log = models.HabitLog(habit_id=habit_id, date=log_date, done=done)
        db.add(new_log)
    db.commit()
    return True

def get_today_logs(db: Session, habit_id: int, today: date):
    return db.query(models.HabitLog).filter(
        models.HabitLog.habit_id == habit_id,
        models.HabitLog.date == today
    ).first()

def get_streak(db: Session, habit_id: int) -> int:
    logs = db.query(models.HabitLog).filter(
        models.HabitLog.habit_id == habit_id
    ).order_by(models.HabitLog.date.desc()).all()
    streak = 0
    for log in logs:
        if log.done:
            streak += 1
        else:
            break
    return streak