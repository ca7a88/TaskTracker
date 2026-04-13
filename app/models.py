from sqlalchemy import Column, Integer, String, Boolean, Date
from app.database import Base

class Habit(Base):
    __tablename__ = "habits"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    frequency = Column(String)  # "daily" or "weekly"
    active = Column(Boolean, default=True)

class HabitLog(Base):
    __tablename__ = "habit_logs"
    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, index=True)
    date = Column(Date)
    done = Column(Boolean, default=False)