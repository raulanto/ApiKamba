from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.db.base import TimeStampedModel


class List(Base, TimeStampedModel):
    __tablename__ = "lists"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    position = Column(Integer, default=0)  # Para ordenar las listas
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=False)

    # Relaciones
    board = relationship("Board", back_populates="lists")
    tasks = relationship("Task", back_populates="list", cascade="all, delete-orphan")

