from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.db import get_db
from app.core.roles import require_role, get_current_user
from app.models.movie import Movie  # nếu bạn có model Movie
from datetime import datetime
import pandas as pd
import os
import shutil

router = APIRouter(prefix="/movies", tags=["movies"])

# Đường dẫn CSV
CSV_PATH = os.path.join("data", "Movies_vi_with_poster.csv")
POSTER_DIR = os.path.join("data", "posters")

os.makedirs(POSTER_DIR, exist_ok=True)

# -----------------------------
# 1️ Thống kê phim
# -----------------------------
@router.get("/stats")
async def get_movie_stats():
    if not os.path.exists(CSV_PATH):
        raise HTTPException(status_code=404, detail="Movies_vi.csv not found")

    df = pd.read_csv(CSV_PATH).fillna("")
    total_movies = len(df)
    unique_directors = df["Director"].nunique()

    all_stars = []
    for stars in df["Stars"]:
        if isinstance(stars, str):
            clean = stars.replace("[", "").replace("]", "").replace("'", "")
            all_stars.extend([s.strip() for s in clean.split(",") if s.strip()])
    top_stars = pd.Series(all_stars).value_counts().head(5).index.tolist()

    all_genres = []
    for g in df["Genres"]:
        if isinstance(g, str):
            clean = g.replace("[", "").replace("]", "").replace("'", "")
            all_genres.extend([x.strip() for x in clean.split(",") if x.strip()])
    genre_count = pd.Series(all_genres).value_counts().head(10)
    top_genres = [{"name": g, "value": int(c)} for g, c in genre_count.items()]

    return JSONResponse(
        content={
            "total_movies": int(total_movies),
            "unique_directors": int(unique_directors),
            "top_stars": top_stars,
            "top_genres": top_genres,
        }
    )

# -----------------------------
# 2️⃣ Danh sách phim (public)
# -----------------------------
@router.get("/list")
async def get_movie_list():
    if not os.path.exists(CSV_PATH):
        raise HTTPException(status_code=404, detail="Movies_vi.csv not found")

    df = pd.read_csv(CSV_PATH).fillna("")
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

# -----------------------------
# 3️⃣ Public test route
# -----------------------------
@router.get("/public")
def public_movies():
    return {"items": ["Little Teo", "Bố Già", "Trạng Quỳnh"]}

# -----------------------------
# 4️⃣ Protected route (user/editor/admin)
# -----------------------------
@router.get("", dependencies=[Depends(require_role(["user", "editor", "admin"]))])
def list_movies(db: Session = Depends(get_db)):
    """Danh sách phim trong hệ thống (chỉ user đã đăng nhập mới xem được)"""
    return {"items": ["Little Teo", "Bố Già", "Trạng Quỳnh"]}

# -----------------------------
# 5️⃣ Admin: Upload phim mới
# -----------------------------
@router.post("/upload", dependencies=[Depends(require_role(["admin"]))])
async def upload_movie(
    title: str = Form(...),
    description: str = Form(""),
    poster: UploadFile = File(None),
):
    """Thêm phim mới (admin only)"""
    poster_filename = None

    # Nếu có file poster
    if poster:
        ext = os.path.splitext(poster.filename)[1]
        poster_filename = f"{datetime.now().timestamp():.0f}{ext}"
        save_path = os.path.join(POSTER_DIR, poster_filename)
        with open(save_path, "wb") as f:
            shutil.copyfileobj(poster.file, f)

    # Ghi phim vào CSV (tạm thời, hoặc DB nếu có)
    df = pd.read_csv(CSV_PATH) if os.path.exists(CSV_PATH) else pd.DataFrame(columns=[
        "Id", "Title", "Original Title", "Release Date", "Director", "Stars", "Genres", "Overview", "PosterFile"
    ])
    new_id = df["Id"].max() + 1 if not df.empty else 1
    new_row = {
        "Id": new_id,
        "Title": title,
        "Original Title": title,
        "Release Date": datetime.now().strftime("%Y-%m-%d"),
        "Director": "",
        "Stars": "",
        "Genres": "",
        "Overview": description,
        "PosterFile": poster_filename,
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(CSV_PATH, index=False)

    return {"msg": "Movie added successfully", "poster": poster_filename}

# -----------------------------
# 6️⃣ Admin: Xóa phim
# -----------------------------
@router.delete("/{movie_id}", dependencies=[Depends(require_role(["admin"]))])
def delete_movie(movie_id: int):
    """Xoá phim (admin only)"""
    if not os.path.exists(CSV_PATH):
        raise HTTPException(status_code=404, detail="Movies_vi.csv not found")

    df = pd.read_csv(CSV_PATH)
    if movie_id not in df["Id"].values:
        raise HTTPException(status_code=404, detail="Movie not found")

    df = df[df["Id"] != movie_id]
    df.to_csv(CSV_PATH, index=False)
    return {"msg": f"Deleted movie id={movie_id}"}
