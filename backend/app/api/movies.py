from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.db import get_db
from app.core.roles import require_role, get_current_user


import pandas as pd
import os

router = APIRouter(prefix="/movies", tags=["movies"])

#  Đường dẫn đến file CSV thật
CSV_PATH = os.path.join("data", "Movies_vi_with_poster.csv")

@router.get("/stats")
async def get_movie_stats():
    """Trả thống kê phim: thể loại, đạo diễn, diễn viên"""
    if not os.path.exists(CSV_PATH):
        raise HTTPException(status_code=404, detail="Movies_vi.csv not found")

    try:
        df = pd.read_csv(CSV_PATH)
        df = df.fillna("")

        #  Tổng số phim
        total_movies = len(df)

        #  Thống kê đạo diễn
        unique_directors = df["Director"].nunique()

        #  Lấy danh sách diễn viên (gộp toàn bộ cột Stars)
        all_stars = []
        for stars in df["Stars"]:
            if isinstance(stars, str):
                # bỏ ký tự [''] nếu có
                clean = stars.replace("[", "").replace("]", "").replace("'", "")
                all_stars.extend([s.strip() for s in clean.split(",") if s.strip()])
        top_stars = pd.Series(all_stars).value_counts().head(5).index.tolist()

        #  Thống kê thể loại
        all_genres = []
        for g in df["Genres"]:
            if isinstance(g, str):
                clean = g.replace("[", "").replace("]", "").replace("'", "")
                all_genres.extend([x.strip() for x in clean.split(",") if x.strip()])
        genre_count = pd.Series(all_genres).value_counts().head(10)
        top_genres = [
            {"name": genre, "value": int(count)} for genre, count in genre_count.items()
        ]

        stats = {
            "total_movies": int(total_movies),
            "unique_directors": int(unique_directors),
            "top_stars": top_stars,
            "top_genres": top_genres,
        }

        return JSONResponse(content=stats)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading CSV: {e}")




@router.get("/list")
async def get_movie_list():
    """Trả về danh sách phim trong CSDL"""
    if not os.path.exists(CSV_PATH):
        raise HTTPException(status_code=404, detail="Movies_vi.csv not found")

    try:
        df = pd.read_csv(CSV_PATH)
        df = df.fillna("")

        movies = []
        for _, row in df.iterrows():
            movies.append({
                "id": int(row["Id"]),
                "title": row["Title"],
                "original_title": row["Original Title"],
                "release_date": row["Release Date"],
                "director": row["Director"],
                "stars": row["Stars"],
                "genres": row["Genres"],
                "overview": row["Overview"][:250] + "...",
                "poster": f"http://localhost:8000/static/{row['PosterFile']}" if isinstance(row["PosterFile"], str) else None,
            })

        return JSONResponse(content={"movies": movies, "total": len(movies)})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading CSV: {e}")



@router.get("/public")
def public_movies():
    return {"items": ["Little Teo", "Bố Già", "Trạng Quỳnh"]}

# protected: user/editor/admin
@router.get("/", dependencies=[Depends(require_role(["user", "editor", "admin"]))])
def list_movies(db: Session = Depends(get_db)):
    # here you would query real movie table; demo only
    return {"items": ["Little Teo", "Bố Già", "Trạng Quỳnh"]}

# admin only
@router.delete("/{movie_id}", dependencies=[Depends(require_role(["admin"]))])
def delete_movie(movie_id: int):
    return {"msg": f"deleted {movie_id}"}