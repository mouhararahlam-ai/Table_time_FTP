from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    DONE = "done"

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    deadline: datetime
    status: TaskStatus = TaskStatus.PENDING

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    status: Optional[TaskStatus] = None

class Task(TaskBase):
    id: int

    class Config:
        from_attributes = True
