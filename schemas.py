from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

MovieGenre = Literal["action", "comedy", "drama", "thriller"]


class MovieCreate(BaseModel):
    movie_id: int
    title: str = Field(min_length=1, max_length=200)
    director: str = Field(min_length=1, max_length=100)
    genre: MovieGenre
    duration: int = Field(gt=0)
    rating: float = Field(ge=0, le=5)


class MovieUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    director: str = Field(min_length=1, max_length=100)
    genre: MovieGenre
    duration: int = Field(gt=0)
    rating: float = Field(ge=0, le=5)


class MovieResponse(BaseModel):
    movie_id: int
    title: str
    director: str
    genre: MovieGenre
    duration: int
    rating: float

    model_config = ConfigDict(from_attributes=True)
