from pydantic import BaseModel
from datetime import date

class HabitCreate(BaseModel):
    name: str
    frequency: str = "daily"

class HabitResponse(BaseModel):
    id: int
    name: str
    frequency: str
    active: bool

    class Config:
        from_attributes = True

class HabitLogCreate(BaseModel):
    habit_id: int
    date: date
    done: bool

class HabitLogResponse(BaseModel):
    id: int
    habit_id: int
    date: date
    done: bool

    class Config:
        from_attributes = True