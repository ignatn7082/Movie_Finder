from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from app.db import get_db
from app.models.movie import Movie
from app.core.roles import require_role
import os, shutil
from datetime import datetime

router = APIRouter(prefix="/movies", tags=["movies"])

# Thư mục chứa poster
POSTER_DIR = os.path.join("data", "posters")
os.makedirs(POSTER_DIR, exist_ok=True)


def movie_to_dict(m: Movie) -> Dict[str, Any]:
    return {
        "id": getattr(m, "id", None),
        "title": getattr(m, "title", "") or getattr(m, "Title", ""),
        "original_title": getattr(m, "original_title", "") or getattr(m, "Original Title", ""),
        "overview": getattr(m, "overview", "") or getattr(m, "Overview", ""),
        "release_date": getattr(m, "release_date", "") or getattr(m, "Release Date", ""),
        "director": getattr(m, "director", "") or getattr(m, "Director", ""),
        "stars": getattr(m, "stars", "") or getattr(m, "Stars", ""),
        "genres": getattr(m, "genres", "") or getattr(m, "Genres", ""),
        "poster": getattr(m, "poster", "") or getattr(m, "PosterFile", ""),
    }


# ================================
#  Lấy danh sách phim (public)
# ================================

@router.get("/list", summary="Danh sách phim (public)", tags=["movies"])
def list_movies(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=200),
    q: str | None = Query(None, description="Từ khoá tìm kiếm theo tiêu đề"),
):
    try:
        query = db.query(Movie)
        if q:
            like_q = f"%{q}%"
            # dùng ILIKE cho Postgres compat
            query = query.filter(func.lower(getattr(Movie, "title")) .like(func.lower(like_q)))
        total = query.count()
        movies = query.offset((page - 1) * per_page).limit(per_page).all()
        return JSONResponse(content={
            "movies": [movie_to_dict(m) for m in movies],
            "total": total,
            "page": page,
            "per_page": per_page
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch movies")




@router.get("", summary="Danh sách phim (compat: /api/movies)")
def list_movies(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=200),
    q: str | None = Query(None, description="Từ khoá tìm kiếm theo tiêu đề"),
):
    try:
        query = db.query(Movie)
        if q:
            like_q = f"%{q.lower()}%"
            # dùng lower/title to support simple case-insensitive search
            query = query.filter(func.lower(getattr(Movie, "title")).like(like_q))
        total = query.count()
        movies = query.offset((page - 1) * per_page).limit(per_page).all()
        return JSONResponse(content={
            "movies": [movie_to_dict(m) for m in movies],
            "total": total,
            "page": page,
            "per_page": per_page
        })
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch movies")


# ==================================
#  Thêm phim mới (admin only)
# ==================================
@router.post("/upload", dependencies=[Depends(require_role(["admin"]))])
async def upload_movie(
    title: str = Form(...),
    description: str = Form(""),
    poster: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    filename = None
    if poster:
        ext = os.path.splitext(poster.filename)[1]
        filename = f"{datetime.now().timestamp():.0f}{ext}"
        path = os.path.join(POSTER_DIR, filename)
        with open(path, "wb") as f:
            shutil.copyfileobj(poster.file, f)

    movie = Movie(original_title=title, overview=description, poster=filename)
    db.add(movie)
    db.commit()
    db.refresh(movie)

    return {"msg": "Movie added successfully", "id": movie.id}


# ==================================
#  Xóa phim (admin only)
# ==================================
@router.delete("/{movie_id}", dependencies=[Depends(require_role(["admin"]))])
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).get(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    # Xóa file poster nếu có
    if movie.poster:
        try:
            os.remove(os.path.join(POSTER_DIR, movie.poster))
        except FileNotFoundError:
            pass

    db.delete(movie)
    db.commit()
    return {"msg": f"Movie id={movie_id} deleted"}


#  Endpoint: Lấy danh sách phim trực tiếp từ PostgreSQL
@router.get("/from-db", dependencies=[Depends(require_role(["user", "editor", "admin"]))])
def get_movies_from_db(db: Session = Depends(get_db)):
    try:
        movies = db.query(Movie).all()
        if not movies:
            raise HTTPException(status_code=404, detail="Không có phim nào trong CSDL")

        data = [
            {
                "id": m.id,
                "title": m.title,
                "original_title": m.original_title,
                "release_date": m.release_date,
                "director": m.director,
                "stars": m.stars,
                "genres": m.genres,
                "overview": m.overview[:250] + "..." if m.overview else "",
                "poster": f"http://localhost:8000/static/{m.poster}"
                if m.poster
                else None,
            }
            for m in movies
        ]

        return {"movies": data, "total": len(data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi truy vấn database: {e}")


#  Endpoint: Lấy chi tiết 1 phim theo ID
@router.get("/from-db/{movie_id}", dependencies=[Depends(require_role(["user", "editor", "admin"]))])
def get_movie_detail(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Không tìm thấy phim")
    return {
        "id": movie.id,
        "title": movie.title,
        "original_title": movie.original_title,
        "release_date": movie.release_date,
        "director": movie.director,
        "stars": movie.stars,
        "genres": movie.genres,
        "overview": movie.overview,
        "poster": f"http://localhost:8000/static/{movie.poster}" if movie.poster else None,
    }


@router.get("/stats", summary="Thống kê phim (public)", tags=["movies"])
def movies_stats(db: Session = Depends(get_db)):
    try:
        total_movies = db.query(func.count(getattr(Movie, "id"))).scalar() or 0
        # distinct directors
        try:
            distinct_directors = db.query(func.count(func.distinct(getattr(Movie, "director")))).scalar() or 0
        except Exception:
            distinct_directors = 0

        # top genres & top stars (simple aggregation in python)
        movies = db.query(Movie).all()
        genre_counts: dict = {}
        star_counts: dict = {}

        for m in movies:
            genres_field = getattr(m, "genres", "") or getattr(m, "Genres", "") or ""
            for g in str(genres_field).split(","):
                g = g.strip()
                if not g:
                    continue
                genre_counts[g] = genre_counts.get(g, 0) + 1

            stars_field = getattr(m, "stars", "") or getattr(m, "Stars", "") or ""
            for s in str(stars_field).split(","):
                s = s.strip()
                if not s:
                    continue
                star_counts[s] = star_counts.get(s, 0) + 1

        top_genres = sorted([{"name": k, "value": v} for k, v in genre_counts.items()], key=lambda x: -x["value"])[:10]
        top_stars = [k for k, _ in sorted(star_counts.items(), key=lambda x: -x[1])[:10]]

        return JSONResponse(content={
            "total_movies": int(total_movies),
            "directors": int(distinct_directors),
            "top_genres": top_genres,
            "top_stars": top_stars
        })
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to compute stats")