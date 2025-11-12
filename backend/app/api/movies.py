from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.movie import Movie
from app.core.roles import require_role
import os, shutil
from datetime import datetime

router = APIRouter(prefix="/movies", tags=["movies"])

# Thư mục chứa poster
POSTER_DIR = os.path.join("data", "posters")
os.makedirs(POSTER_DIR, exist_ok=True)


# ================================
#  Lấy danh sách phim (public)
# ================================
@router.get("", dependencies=[Depends(require_role(["user", "editor", "admin"]))])
def get_movies(db: Session = Depends(get_db)):
    movies = db.query(Movie).order_by(Movie.id.desc()).all()
    return [
        {
            "id": m.id,
            "title": m.title,
            "description": m.overview,
            "poster": f"http://localhost:8000/static/{m.poster}" if m.poster else None,
            "created_at": m.release_date,
        }
        for m in movies
    ]


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