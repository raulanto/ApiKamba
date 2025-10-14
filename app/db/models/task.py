from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum as SQLEnum
import enum
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.db.base import TimeStampedModel


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(Base, TimeStampedModel):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    position = Column(Integer, default=0)  # Para ordenar tareas dentro de una lista
    priority = Column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM)
    list_id = Column(Integer, ForeignKey("lists.id"), nullable=False)

    # Relaciones
    list = relationship("List", back_populates="tasks")
