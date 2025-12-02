# app/services/actor_service.py

import re
from sqlalchemy import or_, func
from sqlalchemy.orm import Session
from app.models.movie import Movie
from app.models.role import Role
from app.db import SessionLocal
from typing import List, Dict, Optional
from app.services.vit_service import ( 
    extract_vit_feature,
    get_all_actor_similarities_vit
)
from app.core.detect_face import detect_and_crop_face
from PIL import Image


def normalize_name_vietnamese_name(name: str) -> str:
    if not name:
        return ""
    name = name.strip().lower()
    name = name.replace('đ', 'd').replace('Đ', 'd')
    trans = str.maketrans(
        'àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ',
        'a'*17 + 'e'*11 + 'i'*5 + 'o'*17 + 'u'*11 + 'y'*5
    )
    name = name.translate(trans)
    name = re.sub(r'[^a-z\s]', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def _build_movie_with_role(movie: Movie, role_name: Optional[str] = None) -> Dict:
    """Chuyển Movie + vai diễn thành dict chuẩn trả về frontend"""
    return {
        "id": movie.id,
        "title": movie.title,
        "original_title": movie.original_title or movie.title,
        "release_date": movie.release_date or "N/A",
        "director": movie.director or "Chưa rõ",
        "genres_vn": movie.genres_vn or "",
        "overview": movie.overview or "Chưa có tóm tắt.",
        "poster": movie.posters,
        "role_name": role_name or "Vai phụ / Chưa rõ",  # Quan trọng: hiển thị vai diễn!
        "year": (movie.release_date or "")[:4]
    }

def get_movies_by_actor(
    db: Session,
    actor_name: str,
    limit: int = 60,
    include_role_name: bool = True
) -> tuple[str | None, List[Dict]]:
    """
    Tìm tất cả phim mà một diễn viên tham gia.
    Dùng được cho cả:
      - Tìm bằng ảnh (đã match face → actor_name chính xác)
      - Tìm bằng text (có fuzzy nếu cần)

    Returns:
        (tên_diễn_viên_thực_tế_trong_DB, danh_sách_phim)
    """
    if not actor_name or not actor_name.strip():
        return None, []

    actor_name = actor_name.strip()

    # Tìm chính xác theo actor_name trong bảng Role
    roles_query = db.query(Role).filter(Role.actor_name == actor_name)

    roles = roles_query.all()
    if not roles:
        return None, []  # Không có trong DB → trả rỗng ngay

    # Lấy danh sách phim, kèm vai diễn
    seen_movie_ids = set()
    movies = []

    for role in roles:
        movie = role.movie
        if not movie or movie.id in seen_movie_ids:
            continue

        seen_movie_ids.add(movie.id)

        movie_dict = _build_movie_with_role(
            movie=movie,
            role_name=role.role_name if include_role_name else None
        )
        movies.append(movie_dict)

        if len(movies) >= limit:
            break

    # Sắp xếp theo năm mới nhất
    movies.sort(key=lambda x: x.get("year", "0000"), reverse=True)

    return actor_name, movies

def query_by_image_actor_mode(
    img_path: str,
    actor_threshold: float = 0.60,     # bạn muốn nhạy hơn → để 0.60 là hợp lý
    top_k_actors: int = 100,
    film_limit: int = 60,
    db: Session = None                  # BẮT BUỘC truyền từ route qua Depends(get_db)
):
    """
    Chế độ TÌM DIỄN VIÊN QUA ẢNH
    → Trả về toàn bộ phim + vai diễn của diễn viên được nhận diện
    """

    # 1. KIỂM TRA DB – BẮT BUỘC (không tự tạo SessionLocal ở đây)
    if db is None:
        return {
            "status": "error",
            "message": "Database session không được cung cấp. Hãy truyền db từ route."
        }

    try:
        pil_img = Image.open(img_path).convert("RGB")
    except Exception as e:
        return {
            "status": "error",
            "message": f"Không thể mở file ảnh: {str(e)}"
        }

    # 2. PHÁT HIỆN KHUÔN MẶT
    cropped_face = detect_and_crop_face(pil_img)
    if not cropped_face:
        return {
            "status": "success",
            "search_mode": "actor",
            "detected_actor": None,
            "actor_filmography": [],
            "actor_similarities": [],
            "message": "Không phát hiện khuôn mặt rõ ràng trong ảnh."
        }

    # 3. TRÍCH XUẤT ĐẶC TRƯNG
    face_feat = extract_vit_feature(cropped_face)
    if face_feat is None:
        return {
            "status": "error",
            "message": "Không trích xuất được đặc trưng khuôn mặt (ảnh mờ hoặc lỗi mô hình)."
        }

    # 4. SO SÁNH VỚI CƠ SỞ DỮ LIỆU DIỄN VIÊN
    top_actors = get_all_actor_similarities_vit(face_feat, top_k_actors=top_k_actors)

    if not top_actors:
        return {
            "status": "success",
            "search_mode": "actor",
            "detected_actor": None,
            "actor_filmography": [],
            "actor_similarities": [],
            "message": "Không tìm thấy diễn viên nào trong hệ thống."
        }

    best_match = top_actors[0]
    best_score = best_match["score"]

    # 5. KIỂM TRA NGƯỠNG TƯƠNG ĐỒNG
    if best_score < actor_threshold:
        return {
            "status": "success",
            "search_mode": "actor",
            "detected_actor": None,
            "actor_filmography": [],
            "actor_similarities": top_actors[:10],
            "message": f"Độ tương đồng chưa đủ (cao nhất: {best_match['actor']} – {best_score:.1%})"
        }

    actor_name = best_match["actor"]

    # 6. LẤY DANH SÁCH PHIM CỦA DIỄN VIÊN (hàm bạn đã viết sẵn)
    real_actor_name, movies = get_movies_by_actor(
        db=db,
        actor_name=actor_name,
        limit=film_limit,
        use_fuzzy=False
    )

    # 7. TRẢ VỀ KẾT QUẢ ĐẸP & AN TOÀN
    if not movies:
        return {
            "status": "success",
            "search_mode": "actor",
            "detected_actor": {
                "name": real_actor_name or actor_name,
                "similarity": round(best_score, 4),
                "total_movies": 0
            },
            "actor_filmography": [],
            "actor_similarities": top_actors[:10],
            "message": f"Nhận diện thành công {real_actor_name or actor_name} nhưng chưa có phim trong CSDL."
        }

    return {
        "status": "success",
        "search_mode": "actor",
        "detected_actor": {
            "name": real_actor_name or actor_name,
            "similarity": round(best_score, 4),
            "total_movies": len(movies)
        },
        "actor_filmography": movies,
        "actor_similarities": top_actors[:10],
        "message": f"Nhận diện thành công: {real_actor_name or actor_name} ({best_score:.1%})"
    }