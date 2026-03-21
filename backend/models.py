from sqlalchemy import Column, Integer, String, DateTime
#from .database import Base
from database import Base
import enum

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    DONE = "done"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    deadline = Column(DateTime)
    status = Column(String, default=TaskStatus.PENDING.value)
