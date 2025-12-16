# app/services/main_search_service.py

import os
import numpy as np
import faiss
from PIL import Image

from app.services.actor_service import query_by_image_actor_mode
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.services.base_service import get_all_actors_in_movie, safe_load_image
from app.core.detect_face import detect_and_crop_face 

# Import ViT loader
from app.core.vit_loader import vit_model, vit_preprocess, extract_feature as extract_vit_feature
from app.services.vit_service import actor_index, actor_labels, query_by_image_vit_feature_content

# ==================================
# HÀM HỖ TRỢ: SO SÁNH VỚI TẤT CẢ DIỄN VIÊN
# ==================================

def get_all_actor_similarities_vit_ivfpq(
    input_feat: np.ndarray,
    top_k_actors: int = 50
) -> List[Dict[str, float]]:
    """
    Dùng FAISS IVFPQ để tìm top K diễn viên – giảm đáng kể số lượng phép tính
    """
    global actor_index, actor_labels

    if actor_index is None or actor_labels is None:
        print("[ERROR] FAISS IVFPQ index chưa load!")
        return []

    if actor_index.ntotal == 0:
        print("[ERROR] Index rỗng!")
        return []

    # Chuẩn bị vector
    feat = input_feat.reshape(1, -1).astype('float32')
    faiss.normalize_L2(feat)

    # Tăng nprobe để chính xác hơn (cân bằng tốc độ/chính xác)
    actor_index.nprobe = 10

    k = min(top_k_actors, actor_index.ntotal)
    D, I = actor_index.search(feat, k)

    results = []
    for dist, idx in zip(D[0], I[0]):
        if idx == -1:
            continue
        actor_name = str(actor_labels[idx]).replace("_", " ")
        results.append({
            "actor": actor_name,
            "score": float(dist)  # IVFPQ + IP → dist là cosine similarity
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results

def get_all_actor_similarities_vit(input_feat: np.ndarray, top_k_actors=50):
    """
    So sánh đặc trưng ảnh đầu vào với TOP K diễn viên gần nhất trong Index Diễn viên ViT.
    Trả về dict: {actor_name: similarity}
    """

    if actor_index is None or not actor_labels:
        print("[ERROR] ViT Actor Index/Labels not loaded for comparison.")
        return {}
        
    feat = input_feat.reshape(1, -1)
    faiss.normalize_L2(feat)
    
    k = min(top_k_actors, actor_index.ntotal)
    D, I = actor_index.search(feat, k)  # D: distance (cosine), I: index
    
    similarities = {}
    for dist, index in zip(D[0], I[0]):
        if index != -1:
            actor_name = str(actor_labels[index]).replace("_", " ")
            sim = 1.0 - dist
            similarities[actor_name] = sim
            
    return similarities

# ==================================
# HÀM CHÍNH: TÌM KIẾM HAI BƯỚC
# ==================================

def get_content_search_results(img_path, content_model="resnet50", top_k=5):
    """Chọn mô hình tìm kiếm nội dung (frame/ViT)."""
    if content_model == "vit":
        return query_by_image_vit_feature_content(img_path, top_k=top_k)
    else:
        return {"movies": [], "message": f"Content model '{content_model}' không hợp lệ."}

# def query_by_image_vit(
#     img_path,
#     top_k=5,
#     actor_threshold=0.8,
#     content_threshold=0.25
# ):
#     """Logic hai bước: tìm phim theo content → nhận dạng diễn viên bằng ViT (chỉ nếu detect được khuôn mặt rõ ràng)"""
    
#     # Load ảnh dưới dạng PIL để dùng cho detect face
#     pil_img = Image.open(img_path).convert("RGB")  # Nên trả về PIL.Image hoặc None
#     if pil_img is None:
#         return {
#             "status": "success",
#             "movies": [],
#             "actor_similarities": [],
#             "message": "Không đọc được ảnh đầu vào."
#         }

#     # ================================
#     # THÊM BƯỚC: PHÁT HIỆN VÀ CẮT KHUÔN MẶT
#     # ================================
#     print("[DEBUG] Đang detect khuôn mặt bằng MTCNN...")
#     cropped_face = detect_and_crop_face(pil_img)

#     if not cropped_face:
#         print("KHÔNG PHÁT HIỆN ĐƯỢC KHUÔN MẶT!")

#         # Vẫn chạy bước tìm phim theo content (giữ logic cũ)
#         content_results = query_by_image_vit_feature_content(img_path, top_k=top_k)
#         movie_list = content_results.get("movies", [])

#         if not movie_list:
#             return {
#                 "status": "success",
#                 "movies": [],
#                 "actor_similarities": [],
#                 "message": content_results.get("message", "Không tìm thấy phim liên quan.")
#             }

#         return {
#             "status": "success",
#             "movies": movie_list,
#             "actor_similarities": [],  # Không hiển thị bảng so sánh diễn viên
#             "message": "Tìm thấy phim liên quan nhưng không phát hiện khuôn mặt để nhận dạng diễn viên."
#         }

#     print(f"[DEBUG] Phát hiện khuôn mặt thành công | size={cropped_face.size}")

#     # ================================
#     # BƯỚC 1: Tìm phim theo nội dung (dùng ảnh gốc để giữ context cảnh)
#     # ================================
#     content_results = query_by_image_vit_feature_content(img_path, top_k=top_k)
#     movie_list = content_results.get("movies", [])

#     if not movie_list:
#         return {
#             "status": "success",
#             "movies": [],
#             "actor_similarities": [],
#             "message": "Phát hiện khuôn mặt nhưng không tìm thấy phim liên quan theo nội dung."
#         }

#     # ================================
#     # BƯỚC 2: Trích xuất đặc trưng từ KHUÔN MẶT ĐÃ CROP (tăng độ chính xác)
#     # ================================
#     print("[DEBUG] Đang trích xuất đặc trưng ViT từ khuôn mặt đã crop...")
#     actor_feat = extract_vit_feature(cropped_face)  # Truyền cropped_face (PIL.Image)

#     if actor_feat is None:
#         print("LỖI: extract_vit_feature trả về None dù đã crop face!")
#         return {
#             "status": "success",
#             "movies": movie_list,
#             "actor_similarities": [],
#             "message": "Phát hiện khuôn mặt nhưng không trích xuất được đặc trưng để nhận dạng diễn viên."
#         }

#     print(f"[DEBUG] Trích xuất đặc trưng thành công | shape={actor_feat.shape}")

#     # === Phần còn lại GIỮ NGUYÊN logic cũ (chỉ chạy khi có actor_feat hợp lệ) ===
#     global_actor_similarities = get_all_actor_similarities_vit(actor_feat, top_k_actors=800)

#     updated_movie_list = []
#     global_best_actor = None
#     global_best_similarity = 0.0

#     for movie in movie_list:
#         movie_title = movie.get("original_title") or movie.get("title")
#         actor_names_in_movie = get_all_actors_in_movie(movie_title)

#         print(f"[DEBUG] Phim: {movie_title}, Diễn viên: {actor_names_in_movie}")

#         movie["actors"] = []

#         best_actor_in_movie = None
#         max_similarity_in_movie = 0.0

#         for actor_name in actor_names_in_movie:
#             normalized_name = str(actor_name).replace("_", " ")
#             sim = global_actor_similarities.get(normalized_name, 0.0)

#             movie["actors"].append({
#                 "actor": actor_name,
#                 "similarity": float(sim)
#             })

#             if sim > max_similarity_in_movie:
#                 max_similarity_in_movie = sim
#                 best_actor_in_movie = actor_name

#             if sim > global_best_similarity:
#                 global_best_similarity = sim
#                 global_best_actor = actor_name

#         if best_actor_in_movie and max_similarity_in_movie >= actor_threshold:
#             movie["matched_actor"] = best_actor_in_movie
#             movie["actor_similarity"] = float(max_similarity_in_movie)
#         else:
#             movie["matched_actor"] = None
#             movie["actor_similarity"] = 0.0

#         updated_movie_list.append(movie)

#     sorted_actors = sorted(
#         global_actor_similarities.items(),
#         key=lambda item: item[1],
#         reverse=True
#     )[:50]

#     message = f"Tìm thấy {len(updated_movie_list)} phim liên quan."
#     if global_best_actor and global_best_similarity >= actor_threshold:
#         message += f" Diễn viên nhận dạng tốt nhất: {global_best_actor.replace('_', ' ')} (độ tương đồng: {global_best_similarity:.2f})"
#     else:
#         message += " Có khuôn mặt nhưng không khớp chắc chắn với diễn viên nào trong database."

#     return {
#         "status": "success",
#         "movies": updated_movie_list,
#         "actor_similarities": sorted_actors,
#         "message": message
#     }


def query_by_image_vit(
    img_path,
    top_k=5,
    actor_threshold=0.8,
    content_threshold=0.25
):
    """Logic hai bước: tìm phim theo content → nhận dạng diễn viên bằng ViT nếu có khuôn mặt"""
    
    # BƯỚC 1: Tìm phim theo nội dung/frame
    content_results = query_by_image_vit_feature_content(img_path, top_k=top_k)
    movie_list = content_results.get("movies", [])

    if not movie_list:
        return {
            "status": "success",
            "movies": [],
            "actor_similarities": [],  # Không có gì
            "message": content_results.get("message", "Không tìm thấy phim liên quan.")
        }

    # Load ảnh để xử lý (dùng chung cho cả hai bước)
    img_tensor = safe_load_image(img_path)
    if img_tensor is None:
        return {
            "status": "success",
            "movies": movie_list,
            "actor_similarities": [],
            "message": "Không đọc được ảnh đầu vào."
        }

    # BƯỚC 2: Trích xuất đặc trưng khuôn mặt bằng ViT
    actor_feat = extract_vit_feature(img_path)  # Hàm này nên trả về None nếu không detect face

    # Trường hợp KHÔNG phát hiện khuôn mặt
    if actor_feat is None:
        # Vẫn trả về danh sách phim (nếu có), nhưng không có thông tin diễn viên
        return {
            "status": "success",
            "movies": movie_list,
            "actor_similarities": [],  # Không hiển thị bảng so sánh diễn viên
            "message": "Tìm thấy phim liên quan nhưng không phát hiện khuôn mặt để nhận dạng diễn viên."
        }

    # === Chỉ chạy phần này nếu CÓ phát hiện khuôn mặt ===
    print("actor_feat shape:", actor_feat.shape)

    # Tính độ tương đồng với tất cả diễn viên trong database
    global_actor_similarities = get_all_actor_similarities_vit(actor_feat, top_k_actors=800)

    updated_movie_list = []
    global_best_actor = None
    global_best_similarity = 0.0

    for movie in movie_list:
        movie_title = movie.get("original_title") or movie.get("title")
        actor_names_in_movie = get_all_actors_in_movie(movie_title)

        print(f"[DEBUG] Phim: {movie_title}, Diễn viên: {actor_names_in_movie}")

        movie["actors"] = []  # Danh sách diễn viên + similarity trong phim này

        best_actor_in_movie = None
        max_similarity_in_movie = 0.0

        for actor_name in actor_names_in_movie:
            normalized_name = str(actor_name).replace("_", " ")
            sim = global_actor_similarities.get(normalized_name, 0.0)

            movie["actors"].append({
                "actor": actor_name,
                "similarity": float(sim)
            })

            if sim > max_similarity_in_movie:
                max_similarity_in_movie = sim
                best_actor_in_movie = actor_name

            if sim > global_best_similarity:
                global_best_similarity = sim
                global_best_actor = actor_name

        # Gán diễn viên khớp tốt nhất cho phim (nếu đạt ngưỡng)
        if best_actor_in_movie and max_similarity_in_movie >= actor_threshold:
            movie["matched_actor"] = best_actor_in_movie
            movie["actor_similarity"] = float(max_similarity_in_movie)
        else:
            movie["matched_actor"] = None
            movie["actor_similarity"] = 0.0

        updated_movie_list.append(movie)

    # Sắp xếp danh sách tất cả diễn viên theo similarity (chỉ khi có face)
    sorted_actors = sorted(
        global_actor_similarities.items(),
        key=lambda item: item[1],
        reverse=True
    )[:50]  # Giới hạn lại để không quá dài (tùy chỉnh nếu cần)

    # Tạo message
    message = f"Tìm thấy {len(updated_movie_list)} phim liên quan."
    if global_best_actor and global_best_similarity >= actor_threshold:
        message += f" Diễn viên nhận dạng tốt nhất: {global_best_actor.replace('_', ' ')} (độ tương đồng: {global_best_similarity:.2f})"
    else:
        message += " Có khuôn mặt nhưng không khớp chắc chắn với diễn viên nào trong database."

    return {
        "status": "success",
        "movies": updated_movie_list,
        "actor_similarities": sorted_actors,  # Chỉ có khi detect face
        "message": message
    }

# ==================================
# HÀM TỔNG HỢP
# ==================================

def query_by_image(
    img_path: str,
    mode: str = "actor",
    top_k: int = 5,
    db: Session = None
) -> dict:
    """
    Hàm tổng hợp chính - 2 chế độ tìm kiếm ảnh
    - mode="actor": Tìm diễn viên → trả về tất cả phim + vai diễn
    - mode="content": Tìm phim theo nội dung ảnh (poster, cảnh phim)
    """
    if not os.path.exists(img_path):
        return {"status": "error", "message": "File ảnh không tồn tại"}

    if mode == "actor":
        return query_by_image_actor_mode(
            img_path=img_path,
            actor_threshold=0.60,
            top_k_actors=100,
            film_limit=60,
            db=db
        )
    elif mode == "content":
        # Nếu bạn chưa có hàm này, tạm trả về kết quả đơn giản
        try:
            return query_by_image_vit(
                img_path=img_path,
                top_k=top_k,
                actor_threshold=0.8,
                content_threshold=0.6
            )
        except Exception as e:
            return {"status": "error", "message": f"Lỗi tìm nội dung: {str(e)}"}
    else:
        return {"status": "error", "message": f"Chế độ không hợp lệ: {mode}"}