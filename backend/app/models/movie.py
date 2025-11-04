from sqlalchemy import Column, Integer, String, DateTime, func
from app.db import Base

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(2000), nullable=True)
    poster = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
