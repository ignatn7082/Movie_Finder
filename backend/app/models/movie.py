from sqlalchemy import Column, Integer, String, DateTime, func
from app.db import Base

# app/models/movie.py
from sqlalchemy import Column, Integer, String, Text
from app.db import Base

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    original_title = Column(String(255))
    release_date = Column(String(50))
    director = Column(String(255))
    stars = Column(Text)
    genres = Column(Text)
    overview = Column(Text)
    poster = Column(String(255))
