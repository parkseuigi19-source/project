from typing import List, Optional, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

# --- User Schemas ---
class UserBase(BaseModel):
    username: str
    user_type: str # 'student', 'jobseeker', 'developer'

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- Todo Schemas ---
class TodoBase(BaseModel):
    text: str
    done: bool = False
    important: bool = False
    meta_info: Optional[dict] = {}

class TodoCreate(TodoBase):
    goal_id: Optional[str] = None

class TodoUpdate(BaseModel):
    text: Optional[str] = None
    done: Optional[bool] = None
    important: Optional[bool] = None
    meta_info: Optional[dict] = None

class Todo(TodoBase):
    id: str
    goal_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# --- Goal Schemas ---
class GoalBase(BaseModel):
    title: str
    description: Optional[str] = None

class GoalCreate(GoalBase):
    user_id: str # For simplicity in MVP, send user_id directly or handle via auth

class Goal(GoalBase):
    id: str
    user_id: str
    progress: int
    created_at: datetime
    todos: List[Todo] = []

    class Config:
        from_attributes = True

# --- Log Schemas ---
class LogBase(BaseModel):
    content: str
    log_type: str

class LogCreate(LogBase):
    user_id: str

class Log(LogBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- Problem Schemas ---
class ProblemBase(BaseModel):
    text: str
    options: List[str] = []
    answer: Optional[str] = None
    explain: Optional[str] = None
    source: Optional[str] = None
    tags: List[str] = []
    important: bool = False

class ProblemCreate(ProblemBase):
    pass

class Problem(ProblemBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
