from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func


class TimeStampedModel:
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
