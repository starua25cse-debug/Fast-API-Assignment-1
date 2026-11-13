from sqlalchemy import Column, Float, Integer, String

from database import Base


class Movie(Base):
    __tablename__ = "movies"

    movie_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    director = Column(String(100), nullable=False)
    genre = Column(String(20), nullable=False)
    duration = Column(Integer, nullable=False)
    rating = Column(Float, nullable=False)
