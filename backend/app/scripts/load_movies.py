import pandas as pd
from sqlalchemy import create_engine
from app.models.movie import Movie
from app.db import Base
from app.core.config import settings

CSV_PATH = "data/Movies_vi_with_poster.csv"

def load_movies():
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)

    df = pd.read_csv(CSV_PATH)
    df = df.fillna("")

    movies = []
    for _, row in df.iterrows():
        movie = {
            "id": row["Id"],
            "title": row["Title"],
            "original_title": row.get("Original Title", ""),
            "release_date": row.get("Release Date", ""),
            "director": row.get("Director", ""),
            "stars": row.get("Stars", ""),
            "genres": row.get("Genres", ""),
            "overview": row.get("Overview", ""),
            "poster": row.get("PosterFile", ""),
        }
        movies.append(movie)

    df_to_insert = pd.DataFrame(movies)
    df_to_insert.to_sql("movies", engine, if_exists="replace", index=False)
    print(f" Đã import {len(df_to_insert)} phim vào database.")

if __name__ == "__main__":
    load_movies()
