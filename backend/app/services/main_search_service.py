# app/services/main_search_service.py

import os
import numpy as np
import faiss
from app.services.resnet_service import query_by_image_resnet50_content
from app.services.base_service import get_all_actors_in_movie, safe_load_image

# Import ViT loader
from app.core.vit_loader import vit_model, vit_preprocess, extract_feature as extract_vit_feature
from app.services.vit_service import actor_index, actor_labels, query_by_image_vit_feature_content

# ==================================
# HÀM HỖ TRỢ: SO SÁNH VỚI TẤT CẢ DIỄN VIÊN
# ==================================

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
    elif content_model == "resnet50":
        return query_by_image_resnet50_content(img_path, top_k=top_k)
    else:
        return {"movies": [], "message": f"Content model '{content_model}' không hợp lệ."}

def query_by_image_two_steps(
    img_path,
    top_k=5,
    content_model="resnet50",
    actor_threshold=0.8,
    content_threshold=0.25
):
    """Logic hai bước, trả về toàn bộ diễn viên + độ tương đồng"""
    # 1. BƯỚC 1: Tìm Content/Frame
    content_results = get_content_search_results(img_path, content_model, top_k)
    movie_list = content_results.get("movies", [])

    if not movie_list:
        return {
            "status": "success",
            "movies": [],
            "actor_similarities": [],
            "message": content_results.get("message", "Không tìm thấy phim liên quan.")
        }

    # 2. BƯỚC 2: Trích xuất đặc trưng khuôn mặt bằng ViT
    img_tensor = safe_load_image(img_path)
    if img_tensor is None:
        return {
            "status": "success",
            "movies": movie_list,
            "actor_similarities": [],
            "message": "Không đọc được ảnh đầu vào."
        }

    actor_feat = extract_vit_feature(img_path)

    if actor_feat is None:
        return {
            "status": "success",
            "movies": movie_list,
            "actor_similarities": [],
            "message": "Tìm thấy phim nhưng không phát hiện khuôn mặt để nhận dạng diễn viên."
        }

    # 2b. Tính độ tương đồng diễn viên toàn cục
    print("actor_feat shape:", None if actor_feat is None else actor_feat.shape)

    global_actor_similarities = get_all_actor_similarities_vit(actor_feat, top_k_actors=400)

    updated_movie_list = []
    global_best_actor = None
    global_best_similarity = 0.0

    for movie in movie_list:
        movie_title = movie.get("original_title") or movie.get("title")
        actor_names_in_movie = get_all_actors_in_movie(movie_title)

        print(f"[DEBUG] Phim: {movie_title}, Diễn viên: {actor_names_in_movie}")

        movie["actors"] = []

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

        if best_actor_in_movie and max_similarity_in_movie >= actor_threshold:
            movie["matched_actor"] = best_actor_in_movie
            movie["actor_similarity"] = float(max_similarity_in_movie)
        else:
            movie["matched_actor"] = None
            movie["actor_similarity"] = 0.0

        updated_movie_list.append(movie)

    sorted_actors = sorted(
        global_actor_similarities.items(),
        key=lambda item: item[1],
        reverse=True
    )

    message = f"Tìm thấy {len(updated_movie_list)} phim."
    if global_best_actor and global_best_similarity >= actor_threshold:
        message += f" Diễn viên tiềm năng tổng thể: {global_best_actor} (Sim: {global_best_similarity:.2f})"
    else:
        message += " Không nhận dạng được diễn viên rõ ràng."

    return {
        "status": "success",
        "movies": updated_movie_list,
        "actor_similarities": sorted_actors,
        "message": message
    }

# ==================================
# HÀM TỔNG HỢP
# ==================================

def query_by_image(img_path, model="two_steps_resnet", top_k=5):
    """Hàm tổng hợp chính, dùng logic hai bước."""
    if model == "two_steps_resnet":
        return query_by_image_two_steps(img_path, top_k=top_k, content_model="resnet50")
    elif model == "two_steps_vit":
        return query_by_image_two_steps(img_path, top_k=top_k, content_model="vit")
    else:
        print(f"Warning: Model '{model}' không được hỗ trợ. Chuyển sang 'two_steps_resnet'.")
        return query_by_image_two_steps(img_path, top_k=top_k, content_model="resnet50")
