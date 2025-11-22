# app/services/base_service.py

import os
import json
import numpy as np
import pandas as pd
from PIL import Image, ImageFile
from app.utils.data_utils import load_movie_metadata
from app.db import SessionLocal
from app.models.role import Role
from app.models.movie import Movie
from sqlalchemy import or_

# Cấu hình chung
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../../data")
STATIC_URL_PREFIX = "http://localhost:8000/static/"
MAX_SIZE = 1024
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Tải dữ liệu cơ sở
movie_df = load_movie_metadata()

def safe_load_image(path):
    """Tải ảnh PIL an toàn và giới hạn kích thước."""
    try:
        img = Image.open(path).convert("RGB")
    except Exception:
        return None

    w, h = img.size
    if max(w, h) > MAX_SIZE:
        scale = MAX_SIZE / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    return img

def get_movie_info(title_or_label: str):
    """Tìm thông tin chi tiết phim từ movie_df."""
    # (Giữ nguyên logic get_movie_info từ search_service.py cũ)
    # ...
    try:
        key = title_or_label.split("_by_")[0].replace("_", " ").strip().lower()
        row = movie_df[movie_df["Original Title"].str.lower() == key]

        if not row.empty:
            record = row.iloc[0]

            poster_file = record.get("PosterFile", "")
            if isinstance(poster_file, float) or not poster_file:
                poster_url = None
            else:
                raw_path = poster_file.replace("\\", "/")
                abs_path = os.path.join(DATA_DIR, raw_path)
                poster_url = f"{STATIC_URL_PREFIX}{raw_path}" if os.path.exists(abs_path) else None

            return {
                "title": record.get("Title", ""),
                "original_title": record.get("Original Title", ""),
                "overview": record.get("Overview", ""),
                "release_date": record.get("Release Date", ""),
                "director": record.get("Director", ""),
                "stars": record.get("Stars", ""),
                "genres_vn": record.get("genres_vn", ""),
                "poster": poster_url,
            }

    except Exception as e:
        print(f"[WARN] Lookup lỗi cho '{title_or_label}': {e}")
        
    return {
        "title": title_or_label,
        "original_title": None,
        "overview": None,
        "release_date": None,
        "director": None,
        "stars": None,
        "genres_vn": None,
        "poster": None,
    }


def search_by_actor_or_role_db(keyword: str):
    """
    Tìm kiếm phim qua bảng roles trong database bằng từ khóa (diễn viên hoặc vai diễn).
    Trả về danh sách phim có chứa thông tin vai diễn.
    """
    db = SessionLocal()
    # Tạo mẫu tìm kiếm: ví dụ nếu keyword là "Thành", sẽ tìm "%thành%"
    keyword_lower = f"%{keyword.lower()}%" 
    
    # Truy vấn: Join Role và Movie, lọc theo actor_name HOẶC role_name
    roles = db.query(Role).join(Movie).filter(
        Role.actor_name.ilike(keyword_lower) | Role.role_name.ilike(keyword_lower)
    ).all()

    results = []
    
    # Lấy thông tin chi tiết cho từng phim tìm thấy
    for r in roles:
        # Sử dụng hàm get_movie_info đã có
        info = get_movie_info(r.movie.title) 
        
        # Thêm thông tin vai diễn khớp
        info["matched_actor"] = r.actor_name
        info["matched_role"] = r.role_name
        info["similarity"] = 1.0 # Độ tương đồng tuyệt đối vì khớp trực tiếp

        # Kiểm tra xem phim này đã được thêm vào results chưa (tránh trùng lặp nếu 1 diễn viên có nhiều vai trong cùng 1 phim)
        is_duplicate = any(res['title'] == info['title'] for res in results)
        
        if not is_duplicate:
            results.append(info)

    db.close()
    return results

def get_actor_movies(actor_name: str):
    """Lấy tất cả phim + vai diễn của diễn viên từ DB."""
    db = SessionLocal()
    rows = (
        db.query(Role, Movie)
        .join(Movie, Role.movie_id == Movie.id)
        .filter(Role.actor_name.ilike(actor_name))
        .all()
    )
    db.close()

    return [
        {
            "movie_id": movie.id,
            "title": movie.title,
            "role_name": role.role_name,
            "poster": movie.poster,
            "release_date": movie.release_date,
        }
        for role, movie in rows
    ]

def normalize(vecs: np.ndarray):
    """Chuẩn hóa L2 cho NumPy array."""
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    return vecs / (norms + 1e-8)


def query_by_keyword(keyword: str, top_k: int = 5):
    """
    Tìm kiếm phim theo từ khóa (tên phim, diễn viên, nhân vật, đạo diễn, thể loại)
    """
    db = SessionLocal()
    keyword = keyword.strip().lower()
    results = []

    try:
        #  Tìm phim khớp trực tiếp trong Movie
        movie_matches = db.query(Movie).filter(
            or_(
                Movie.title.ilike(f"%{keyword}%"),
                Movie.original_title.ilike(f"%{keyword}%"),
                Movie.director.ilike(f"%{keyword}%"),
                Movie.stars.ilike(f"%{keyword}%"),
                Movie.genres_vn.ilike(f"%{keyword}%"),
                Movie.overview.ilike(f"%{keyword}%"),
            )
        ).limit(top_k).all()

        for m in movie_matches:
            results.append({
                "title": m.title,
                "original_title": m.original_title,
                "overview": m.overview,
                "release_date": m.release_date,
                "director": m.director,
                "stars": m.stars,
                "genres_vn": m.genres_vn,
                "poster": f"http://localhost:8000/static/{m.poster}" if m.poster else None,
                "match_type": "movie",
            })

        # 2 Tìm trong bảng Role (actor_name hoặc role_name)
        role_matches = db.query(Role).filter(
            or_(
                Role.actor_name.ilike(f"%{keyword}%"),
                Role.role_name.ilike(f"%{keyword}%")
            )
        ).limit(top_k * 2).all()

        for r in role_matches:
            movie = db.query(Movie).filter(Movie.id == r.movie_id).first()
            if movie:
                results.append({
                    "title": movie.title,
                    "original_title": movie.original_title,
                    "actor": r.actor_name,
                    "role": r.role_name,
                    "poster": f"http://localhost:8000/static/{movie.poster}" if movie.poster else None,
                    "match_type": "role",
                })

    finally:
        db.close()

    #  Gộp kết quả & loại trùng
    unique = {f"{r.get('title')}-{r.get('match_type')}": r for r in results}
    return list(unique.values())[:top_k]