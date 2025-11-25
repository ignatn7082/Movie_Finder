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
import re   
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


def normalize_vi_string(text: str) -> str:
    """
    Chuẩn hóa chuỗi tiếng Việt: chuyển về chữ thường, bỏ dấu, và loại bỏ khoảng trắng/ký tự đặc biệt (kể cả dấu gạch dưới).
    Ví dụ: "Thiên Thần Hộ Mệnh" -> "thienthanhomenh"
            "Thien_Than_Ho_Menh" -> "thienthanhomenh"
    """
    if not isinstance(text, str):
        return ""

    text = text.lower()
    
    # Bỏ dấu tiếng Việt (Cách đơn giản hóa, có thể dùng thư viện unidecode nếu được cài đặt)
    # Mapping cho các chữ cái có dấu
    text = text.replace('á', 'a').replace('à', 'a').replace('ả', 'a').replace('ã', 'a').replace('ạ', 'a')
    text = text.replace('ă', 'a').replace('ắ', 'a').replace('ằ', 'a').replace('ẳ', 'a').replace('ẵ', 'a').replace('ặ', 'a')
    text = text.replace('â', 'a').replace('ấ', 'a').replace('ầ', 'a').replace('ẩ', 'a').replace('ẫ', 'a').replace('ậ', 'a')
    text = text.replace('é', 'e').replace('è', 'e').replace('ẻ', 'e').replace('ẽ', 'e').replace('ẹ', 'e')
    text = text.replace('ê', 'e').replace('ế', 'e').replace('ề', 'e').replace('ể', 'e').replace('ễ', 'e').replace('ệ', 'e')
    text = text.replace('í', 'i').replace('ì', 'i').replace('ỉ', 'i').replace('ĩ', 'i').replace('ị', 'i')
    text = text.replace('ó', 'o').replace('ò', 'o').replace('ỏ', 'o').replace('õ', 'o').replace('ọ', 'o')
    text = text.replace('ô', 'o').replace('ố', 'o').replace('ồ', 'o').replace('ổ', 'o').replace('ỗ', 'o').replace('ộ', 'o')
    text = text.replace('ơ', 'o').replace('ớ', 'o').replace('ờ', 'o').replace('ở', 'o').replace('ỡ', 'o').replace('ợ', 'o')
    text = text.replace('ú', 'u').replace('ù', 'u').replace('ủ', 'u').replace('ũ', 'u').replace('ụ', 'u')
    text = text.replace('ư', 'u').replace('ứ', 'u').replace('ừ', 'u').replace('ử', 'u').replace('ữ', 'u').replace('ự', 'u')
    text = text.replace('ý', 'y').replace('ỳ', 'y').replace('ỷ', 'y').replace('ỹ', 'y').replace('ỵ', 'y')
    text = text.replace('đ', 'd')

    # Loại bỏ các ký tự không phải chữ cái và số (bao gồm cả dấu gạch dưới và khoảng trắng)
    return re.sub(r'[^a-z0-9]', '', text)

def get_movie_info(title: str):
    """
    Lấy thông tin chi tiết phim từ CSDL PostgreSQL qua SQLAlchemy.
    title (param) = key từ FAISS (ví dụ: Thien_Than_Ho_Menh)
    """
    
    # 1. Chuẩn hóa khóa tìm kiếm từ FAISS
    normalized_search_key = normalize_vi_string(title) # --> "thienthanhomenh"

    with SessionLocal() as db:
        # Tải tất cả các bản ghi phim để so sánh chuẩn hóa (Cách này hoạt động, nhưng không tối ưu cho DB lớn)
        all_movies = db.query(Movie).all()
        
        movie = None
        for m in all_movies:
            
            # 2. Chuẩn hóa các trường so sánh trong CSDL
            # DB.original_title: "Thiên Thần Hộ Mệnh" HOẶC "Thien_Than_Ho_Menh"
            normalized_original_title = normalize_vi_string(m.original_title)
            # DB.title: Tên tiếng Việt (Có thể đã bị rút gọn hoặc vẫn còn dấu gạch dưới)
            normalized_title = normalize_vi_string(m.title)
            
            # 3. So sánh chuẩn hóa: Nếu khóa FAISS khớp với Original Title HOẶC Title đã chuẩn hóa
            if normalized_search_key == normalized_original_title or normalized_search_key == normalized_title:
                movie = m
                break
        
        if not movie:
            return None
            
        # Lấy tên hiển thị: Sử dụng trường movie.title
        display_title = movie.title 
        
        # Đảm bảo tên hiển thị cho người dùng không có dấu gạch dưới (chuyển Thien_Than_Ho_Menh thành Thien Than Ho Menh nếu cần)
        if isinstance(display_title, str):
            display_title = display_title.replace('_', ' ')
            
        return {
            "title": display_title, # Tên hiển thị đầy đủ, có dấu cách
            "original_title": movie.original_title, # Key gốc từ CSDL (Thiên Thần Hộ Mệnh HOẶC Thien_Than_Ho_Menh)
            "overview": movie.overview,
            "director": movie.director,
            "genres_vn": movie.genres_vn,
            "stars": movie.stars,
            "poster": f"http://localhost:8000/static/{movie.poster}" if movie.poster else None,
            "release_date": str(movie.release_date) if movie.release_date else None,
        }

# def get_movie_info(title: str):
#     """
#     Lấy thông tin chi tiết phim từ CSDL PostgreSQL qua SQLAlchemy.
#     Truy vấn theo title hoặc original_title (ilike).
#     """

#     search_key = title.strip().lower()

#     with SessionLocal() as db:
#         try:
#             # Truy vấn giống cách gọi search_by_actor_or_role_db
#             movie_record = db.query(Movie).filter(
#                 (Movie.title.ilike(search_key)) |
#                 (Movie.original_title.ilike(search_key))
#             ).first()

#             if movie_record:
#                 # Chuyển object ORM thành dict
#                 movie_data = {
#                     "movie_id": movie_record.id,
#                     "title": movie_record.title,
#                     "original_title": movie_record.original_title,
#                     "overview": movie_record.overview,
#                     "release_date": movie_record.release_date,
#                     "director": movie_record.director,
#                     "stars": movie_record.stars,
#                     "genres_vn": movie_record.genres_vn,
#                     "poster": movie_record.poster
#                 }

#                 # Xử lý poster
#                 poster = movie_data.get("poster")

#                 if isinstance(poster, (float, type(None))) or not poster:
#                     poster_url = None
#                 else:
#                     raw_path = poster.replace("\\", "/")
#                     abs_path = os.path.join(DATA_DIR, raw_path)

#                     poster_url = (
#                         f"{STATIC_URL_PREFIX}{raw_path}"
#                         if os.path.exists(abs_path)
#                         else None
#                     )

#                 # Kết quả cuối cùng
#                 return {
#                     "movie_id": movie_data["movie_id"],
#                     "title": movie_data["title"],
#                     "original_title": movie_data["original_title"],
#                     "overview": movie_data["overview"],
#                     "release_date": movie_data["release_date"],
#                     "director": movie_data["director"],
#                     "stars": movie_data["stars"],
#                     "genres_vn": movie_data["genres_vn"],
#                     "poster": poster,
#                 }

#         except Exception as e:
#             print(f"[WARN] Lỗi get_movie_info('{title}') → {e}")

#     # Không tìm thấy → trả về rỗng
#     return {
#         "title": title,
#         "original_title": None,
#         "overview": None,
#         "release_date": None,
#         "director": None,
#         "stars": None,
#         "genres_vn": None,
#         "poster": None,
#     }



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
            "director": movie.director,
            "stars": movie.stars,
            "genres_vn": movie.genres_vn,
            "overview": movie.overview,
            "original_title": movie.original_title,
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


def get_all_actors_in_movie(movie_title: str) -> list:
    """
    Lấy danh sách tất cả diễn viên (actor_name) tham gia một bộ phim
    từ CSDL hoặc DataFrame Role/Movie.
    """
    with SessionLocal() as db:
        # 1. Tìm Movie ID
        movie = db.query(Movie).filter(Movie.original_title == movie_title).first()
        if not movie:
            movie = db.query(Movie).filter(Movie.title == movie_title).first()
        
        if not movie:
            return []
            
        movie_id = movie.id
        
        # 2. Tìm tất cả Role cho Movie ID đó
        roles = db.query(Role).filter(Role.movie_id == movie_id).all()
        
        # 3. Trả về danh sách tên diễn viên duy nhất
        return list(set([role.actor_name for role in roles if role.actor_name]))
    
