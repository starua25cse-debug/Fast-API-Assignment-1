from typing import Annotated, Literal

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine
from models import Movie
from schemas import MovieCreate, MovieResponse, MovieUpdate

# Create the database table when the application starts.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Movie Collection API",
    description="A Movie Collection API built with FastAPI, Pydantic, and SQLite.",
    version="1.0.0",
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


# return all movies


@app.get(
    "/movies",
    response_model=list[MovieResponse],
    status_code=status.HTTP_200_OK,
)
def get_all_movies(db: db_dependency):
    return db.query(Movie).all()


# sort movies


@app.get(
    "/movies/sort",
    response_model=list[MovieResponse],
    status_code=status.HTTP_200_OK,
)
def sort_movies(
    db: db_dependency,
    sort_by: Literal["duration", "rating"] = Query(default="rating"),
    order: Literal["asc", "desc"] = Query(default="desc"),
):
    sort_column = getattr(Movie, sort_by)

    if order == "asc":
        return db.query(Movie).order_by(sort_column.asc()).all()

    return db.query(Movie).order_by(sort_column.desc()).all()


# return a single movie


@app.get(
    "/movies/{movie_id}",
    response_model=MovieResponse,
    status_code=status.HTTP_200_OK,
)
def get_movie(movie_id: int, db: db_dependency):
    movie = db.get(Movie, movie_id)

    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found",
        )

    return movie


# Create a movie


@app.post(
    "/create_movies",
    response_model=MovieResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_movie(new_movie: MovieCreate, db: db_dependency):
    movie = Movie(**new_movie.model_dump())

    try:
        db.add(movie)
        db.commit()
        db.refresh(movie)
        return movie

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A movie with movie_id {new_movie.movie_id} already exists",
        )

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create movie",
        )


# Update movie


@app.put(
    "/movies/{movie_id}",
    response_model=MovieResponse,
    status_code=status.HTTP_200_OK,
)
def update_movie(movie_id: int, updated_movie: MovieUpdate, db: db_dependency):
    movie = db.get(Movie, movie_id)

    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found",
        )

    update_data = updated_movie.model_dump()

    try:
        for key, value in update_data.items():
            setattr(movie, key, value)

        db.commit()
        db.refresh(movie)
        return movie

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update movie",
        )


# Delete movie


@app.delete(
    "/movies/{movie_id}",
    status_code=status.HTTP_200_OK,
)
def delete_movie(movie_id: int, db: db_dependency):
    movie = db.get(Movie, movie_id)

    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found",
        )

    try:
        db.delete(movie)
        db.commit()
        return {"message": f"Movie with movie_id {movie_id} deleted successfully"}

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete movie",
        )
