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
    get_all_actor_similarities_vit,
    get_similarities_vit
)
from app.core.detect_face import detect_and_crop_face,crop_face
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
        "poster": movie.poster,
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
    actor_threshold: float = 0.60,   # Giữ lại để tham khảo, nhưng không dùng để loại bỏ
    top_k_actors: int = 100,
    film_limit: int = 60,
    db: Session = None
):
    if db is None:
        print("LỖI: db = None → không thể lấy phim từ CSDL!")
        return {"status": "error", "message": "Database session không được cung cấp."}

    try:
        pil_img = Image.open(img_path).convert("RGB")
        print(f"[DEBUG] Ảnh mở thành công | size={pil_img.size}")
    except Exception as e:
        print(f"[ERROR] Không mở được ảnh: {e}")
        return {"status": "error", "message": f"Không mở được ảnh: {e}"}

    # Phát hiện khuôn mặt
    print("[DEBUG] Đang detect khuôn mặt bằng MTCNN...")
    cropped_face = detect_and_crop_face(pil_img)

    if not cropped_face:
        print("KHÔNG PHÁT HIỆN ĐƯỢC KHUÔN MẶT!")
        return {
            "status": "success",
            "search_mode": "actor",
            "detected_actor": None,
            "actor_filmography": [],
            "message": "Không phát hiện khuôn mặt rõ ràng trong ảnh."
        }

    print(f"[DEBUG] Phát hiện khuôn mặt thành công | size={cropped_face.size}")

    # Trích xuất đặc trưng
    print("[DEBUG] Đang trích xuất đặc trưng ViT...")
    face_feat = extract_vit_feature(cropped_face)
    if face_feat is None:
        print("LỖI: extract_vit_feature trả về None!")
        return {"status": "error", "message": "Không trích xuất được đặc trưng khuôn mặt."}

    print(f"[DEBUG] Trích xuất đặc trưng thành công | shape={face_feat.shape}")

    # So sánh với CSDL
    print(f"[DEBUG] Đang tìm {top_k_actors} diễn viên giống nhất...")
    top_actors = get_similarities_vit(face_feat, top_k_actors=top_k_actors)

    if not top_actors:
        print("KHÔNG TÌM THẤY DIỄN VIÊN NÀO TRONG INDEX!")
        return {
            "status": "success",
            "search_mode": "actor",
            "detected_actor": None,
            "actor_filmography": [],
            "message": "Không tìm thấy diễn viên nào trong hệ thống."
        }

    best = top_actors[0]
    actor_name = best["actor"]
    similarity = best["score"]

    print(f"[RESULT] Diễn viên giống nhất: {actor_name} | độ tương đồng: {similarity:.1%}")

    # Lấy phim từ DB (dù độ tương đồng thấp)
    print(f"[DEBUG] Đang truy vấn phim của '{actor_name}' trong CSDL...")
    real_name, movies = get_movies_by_actor(db=db, actor_name=actor_name, limit=film_limit)

    total_movies = len(movies)
    print(f"[DEBUG] Tìm thấy {total_movies} phim của '{real_name or actor_name}'")

    # LUÔN TRẢ VỀ DIỄN VIÊN CAO NHẤT – DÙ DƯỚI NGƯỠNG
    return {
        "status": "success",
        "search_mode": "actor",
        "detected_actor": {
            "name": real_name or actor_name,
            "similarity": round(similarity, 4),
            "total_movies": total_movies,
            "confidence_note": "low" if similarity < actor_threshold else "high"
        },
        "actor_filmography": movies,
        "actor_similarities": top_actors[:10],
        "message": (
            f"Tìm thấy: {real_name or actor_name} "
            f"({similarity:.1%} tương đồng)"
            + (f"  Độ tin cậy thấp" if similarity < actor_threshold else "")
        )
    }


# def query_by_image_actor_mode(
#     img_path: str,
#     actor_threshold: float = 0.60,
#     top_k_actors: int = 100,
#     film_limit: int = 60,
#     db: Session = None
# ):
#     if db is None:
#         print("LỖI: db = None → không thể lấy phim từ CSDL!")
#         return {"status": "error", "message": "Database session không được cung cấp."}

#     try:
#         pil_img = Image.open(img_path).convert("RGB")
#         print(f"[DEBUG] Ảnh mở thành công | size={pil_img.size}")
#     except Exception as e:
#         print(f"[ERROR] Không mở được ảnh: {e}")
#         return {"status": "error", "message": f"Không mở được ảnh: {e}"}

#     # Phát hiện khuôn mặt
#     print("[DEBUG] Đang detect khuôn mặt bằng MTCNN...")
#     cropped_face = detect_and_crop_face(pil_img)

#     if not cropped_face:
#         print("KHÔNG PHÁT HIỆN ĐƯỢC KHUÔN MẶT!")
#         return {
#             "status": "success",
#             "search_mode": "actor",
#             "detected_actor": None,
#             "actor_filmography": [],
#             "message": "Không phát hiện khuôn mặt rõ ràng trong ảnh."
#         }

#     print(f"[DEBUG] Phát hiện khuôn mặt thành công | size={cropped_face.size}")

#     # Trích xuất đặc trưng
#     print("[DEBUG] Đang trích xuất đặc trưng ViT...")
#     face_feat = extract_vit_feature(cropped_face)
#     if face_feat is None:
#         print("LỖI: extract_vit_feature trả về None!")
#         return {"status": "error", "message": "Không trích xuất được đặc trưng khuôn mặt."}

#     print(f"[DEBUG] Trích xuất đặc trưng thành công | shape={face_feat.shape}")

#     # So sánh bằng IVFPQ – giảm số lượng phép tính
#     print(f"[DEBUG] Đang tìm {top_k_actors} diễn viên giống nhất bằng IVFPQ...")
#     top_actors = get_similarities_vit(face_feat, top_k_actors=top_k_actors)

#     if not top_actors:
#         print("KHÔNG TÌM THẤY DIỄN VIÊN NÀO TRONG INDEX!")
#         return {
#             "status": "success",
#             "search_mode": "actor",
#             "detected_actor": None,
#             "actor_filmography": [],
#             "message": "Không tìm thấy diễn viên nào trong hệ thống."
#         }

#     best = top_actors[0]
#     actor_name = best["actor"]
#     similarity = best["score"]
#     actor_name = re.sub(r'image\s*\d+\.jpg\s*\(\)', '', actor_name).strip()
#     print(f"[RESULT] Diễn viên giống nhất: {actor_name} | độ tương đồng: {similarity:.1%}")

#     # Lấy phim từ DB (luôn lấy, dù dưới ngưỡng)
#     print(f"[DEBUG] Đang truy vấn phim của '{actor_name}' trong CSDL...")
#     real_name, movies = get_movies_by_actor(db=db, actor_name=actor_name, limit=film_limit)

#     total_movies = len(movies)
#     print(f"[DEBUG] Tìm thấy {total_movies} phim của '{real_name or actor_name}'")

#     # LUÔN TRẢ VỀ DIỄN VIÊN GIỐNG NHẤT – KHÔNG LOẠI BỎ DÙ DƯỚI NGƯỠNG
#     return {
#         "status": "success",
#         "search_mode": "actor",
#         "detected_actor": {
#             "name": real_name or actor_name,
#             "similarity": round(similarity, 4),
#             "total_movies": total_movies,
#             "confidence_note": "low" if similarity < actor_threshold else "high"
#         },
#         "actor_filmography": movies,
#         "actor_similarities": top_actors[:10],
#         "message": (
#             f"Tìm thấy: {real_name or actor_name} "
#             f"({similarity:.1%} tương đồng)"
#             + (f" – Độ tin cậy thấp" if similarity < actor_threshold else "")
#         )
#     }