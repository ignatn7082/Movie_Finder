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
            "description": m.description,
            "poster": f"http://localhost:8000/static/{m.poster}" if m.poster else None,
            "created_at": m.created_at,
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

    movie = Movie(title=title, description=description, poster=filename)
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
