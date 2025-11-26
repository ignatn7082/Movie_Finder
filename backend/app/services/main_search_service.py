# app/services/main_search_service.py

# Import các hàm từ các service 
import os
import numpy as np
import faiss
from app.services.clip_service import query_actor_by_image_clip,extract_face_clip_feature, extract_clip_feature_content,get_all_actor_similarities_clip, ACTOR_INDEX_PATH, ACTOR_LABELS_JSON
from app.services.resnet_service import query_by_image_resnet50_content, query_by_image_resnet50
from app.services.base_service import get_all_actors_in_movie, safe_load_image

# ==================================
# HÀM HỖ TRỢ: SO SÁNH VỚI TẤT CẢ DIỄN VIÊN
# ==================================

def get_all_actor_similarities(input_feat: np.ndarray, top_k_actors=50):
    """
    So sánh đặc trưng ảnh đầu vào với TOP K diễn viên gần nhất trong Index Diễn viên CLIP.
    Trả về dict: {actor_name: similarity}
    """
    # ACTOR_INDEX và ACTOR_LABELS được import từ clip_service
    if ACTOR_INDEX_PATH is None or not ACTOR_LABELS_JSON:
        print("[ERROR] CLIP Actor Index/Labels not loaded for comparison.")
        return {}
        
    feat = input_feat.reshape(1, -1)
    faiss.normalize_L2(feat)
    
    k = min(top_k_actors, ACTOR_INDEX_PATH.ntotal)
    D, I = ACTOR_INDEX_PATH.search(feat, k) # D: distance (khoảng cách cosine), I: index
    
    similarities = {}
    for dist, index in zip(D[0], I[0]):
        if index != -1:
            # Lấy tên diễn viên và chuẩn hóa
            actor_name = str(ACTOR_LABELS_JSON[index]).replace("_", " ")
            # Cosine Similarity = 1 - Cosine Distance
            sim = 1.0 - dist 
            similarities[actor_name] = sim
            
    return similarities


# ==================================
# HÀM CHÍNH: TÌM KIẾM HAI BƯỚC
# ==================================

def get_content_search_results(img_path, content_model="resnet50", top_k=5):
    """Chọn mô hình tìm kiếm nội dung (frame/clip)."""
    if content_model == "clip":
        return extract_clip_feature_content(img_path, top_k=top_k)
    elif content_model == "resnet50":
        return query_by_image_resnet50_content(img_path, top_k=top_k)
    else:
        return {"movies": [], "message": f"Content model '{content_model}' không hợp lệ."}


# def query_by_image_two_steps(img_path, top_k=5, content_model="resnet50", actor_threshold=0.8, content_threshold=0.25):
#     """
#     Thực hiện logic tìm kiếm 2 bước: 
#     1. Tìm Content/Frame (dùng content_model: resnet50/clip)
#     2. Gắn Diễn viên tốt nhất cho TỪNG PHIM (luôn dùng CLIP Actor Index)
#     """
    
#     # 1. BƯỚC 1: Tìm Content/Frame
#     content_results = get_content_search_results(img_path, content_model, top_k) 
#     movie_list = content_results.get("movies", [])
    
#     if not movie_list:
#         return {
#             "status": "success",
#             "movies": [],
#             "actor_similarities": [],
#             "message": content_results.get("message", "Không tìm thấy phim liên quan.")
#         }

#     # 2. BƯỚC 2: So sánh đặc trưng khuôn mặt với diễn viên
    
#     # 2a. Trích xuất đặc trưng khuôn mặt từ ảnh đầu vào (đặc trưng CLIP)
#     actor_feat = extract_face_clip_feature(img_path)
    
#     # *** KIỂM TRA LỖI NoneType (ĐÃ SỬA) ***
#     if actor_feat is None: 
#         return {
#             "status": "success", 
#             "movies": movie_list, 
#             "actor_similarities": [],
#             "message": "Tìm thấy phim, nhưng không thể nhận dạng diễn viên (Không phát hiện khuôn mặt)."
#         }

#     # 2b. LẤY ĐỘ TƯƠNG ĐỒNG TOÀN CẦU (CHỈ MỘT LẦN)
#     # Tìm Top K diễn viên gần nhất trong Index Diễn viên CLIP toàn cầu (tối ưu hóa)
#     # Hàm này thực hiện FAISS search một lần duy nhất
#     global_actor_similarities = get_all_actor_similarities_clip(actor_feat, top_k_actors=50) 

#     # 2c. TRA CỨU VÀ GẮN DIỄN VIÊN TỐT NHẤT vào TỪNG PHIM (Lọc theo phim)
    
#     global_best_actor = None
#     global_best_similarity = 0.0
    
#     updated_movie_list = []
    
#     for movie in movie_list:
#         movie_title = movie.get("original_title") or movie.get("title")
        
#         # Lấy danh sách diễn viên của phim (chỉ những diễn viên này mới được quan tâm)
#         actor_names_in_movie = get_all_actors_in_movie(movie_title)
#         print(f"[DEBUG] Phim: {movie_title}, Diễn viên: {actor_names_in_movie}") 

#         best_actor_in_movie = None
#         max_similarity_in_movie = 0.0

#         for actor_name in actor_names_in_movie:
#             # TRA CỨU độ tương đồng đã tính sẵn từ index toàn cầu
#             normalized_actor_name = str(actor_name).replace("_", " ") 
#             sim = global_actor_similarities.get(normalized_actor_name, 0.0) 
            
#             # Cập nhật diễn viên tốt nhất trong phim
#             if sim > max_similarity_in_movie:
#                 max_similarity_in_movie = sim
#                 best_actor_in_movie = actor_name
            
#             # Cập nhật diễn viên tốt nhất TỔNG THỂ
#             if sim > global_best_similarity:
#                 global_best_similarity = sim
#                 global_best_actor = actor_name
#                 print(f"[DEBUG] Cập nhật diễn viên tốt nhất TỔNG THỂ: {global_best_actor} (Sim: {global_best_similarity:.2f})")
        
#         # Thêm thông tin diễn viên tốt nhất vào đối tượng phim
#         if best_actor_in_movie and max_similarity_in_movie >= actor_threshold:
#             movie["matched_actor"] = best_actor_in_movie
#             movie["actor_similarity"] = float(max_similarity_in_movie)
#         else:
#             movie["matched_actor"] = None 
#             movie["actor_similarity"] = 0.0
            
#         updated_movie_list.append(movie)

#     # 3. Chuẩn bị kết quả cuối cùng 
    
#     sorted_actors = sorted(global_actor_similarities.items(), key=lambda item: item[1], reverse=True)
    
#     # Cập nhật message
#     message = f"Tìm thấy {len(updated_movie_list)} phim liên quan."
#     if global_best_actor and global_best_similarity >= actor_threshold:
#         message += f" Diễn viên tiềm năng TỔNG THỂ: {global_best_actor} (Sim: {global_best_similarity:.2f})"
#     else:
#         message += " Không nhận dạng được diễn viên rõ ràng trong các phim này."
        
#     return {
#         "status": "success",
#         "movies": updated_movie_list, 
#         "actor_similarities": sorted_actors, 
#         "message": message,
#     }


def query_by_image_two_steps(
    img_path,
    top_k=5,
    content_model="resnet50",
    actor_threshold=0.8,
    content_threshold=0.25
):
    """
    Bản nâng cấp:
    → Trả về toàn bộ diễn viên của mỗi phim cùng độ tương đồng
    → Vẫn giữ matched_actor (diễn viên phù hợp nhất của từng phim)
    """

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

    # 2. BƯỚC 2: Trích xuất đặc trưng CLIP khuôn mặt
    actor_feat = extract_face_clip_feature(img_path)

    if actor_feat is None:
        return {
            "status": "success",
            "movies": movie_list,
            "actor_similarities": [],
            "message": "Tìm thấy phim nhưng không phát hiện khuôn mặt để nhận dạng diễn viên."
        }

    # 2b. Tính độ tương đồng diễn viên toàn cục
    global_actor_similarities = get_all_actor_similarities_clip(
        actor_feat, top_k_actors=400
    )

    updated_movie_list = []
    global_best_actor = None
    global_best_similarity = 0.0

    # 2c. Với từng phim: duyệt TẤT CẢ diễn viên
    for movie in movie_list:
        movie_title = movie.get("original_title") or movie.get("title")
        actor_names_in_movie = get_all_actors_in_movie(movie_title)

        print(f"[DEBUG] Phim: {movie_title}, Diễn viên: {actor_names_in_movie}")

        # tạo danh sách FULL diễn viên với similarity
        movie["actors"] = []

        best_actor_in_movie = None
        max_similarity_in_movie = 0.0

        for actor_name in actor_names_in_movie:
            normalized_name = str(actor_name).replace("_", " ")
            sim = global_actor_similarities.get(normalized_name, 0.0)

            # Thêm vào danh sách diễn viên của phim
            movie["actors"].append({
                "actor": actor_name,
                "similarity": float(sim)
            })

            # Tìm diễn viên tốt nhất của phim
            if sim > max_similarity_in_movie:
                max_similarity_in_movie = sim
                best_actor_in_movie = actor_name

            # Tìm diễn viên tốt nhất tổng thể
            if sim > global_best_similarity:
                global_best_similarity = sim
                global_best_actor = actor_name
                print(f"[DEBUG] Best tổng thể → {global_best_actor} ({global_best_similarity:.2f})")

        # Gắn kết luận diễn viên tốt nhất của phim
        if best_actor_in_movie and max_similarity_in_movie >= actor_threshold:
            movie["matched_actor"] = best_actor_in_movie
            movie["actor_similarity"] = float(max_similarity_in_movie)
        else:
            movie["matched_actor"] = None
            movie["actor_similarity"] = 0.0

        updated_movie_list.append(movie)

    # Chuẩn bị kết quả trả về
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



# Thay thế hàm query_by_image cũ bằng logic mới (Mặc định dùng ResNet50 cho bước 1)
def query_by_image(img_path, model="two_steps_resnet", top_k=5):
    """Hàm tổng hợp chính, chỉ dùng logic hai bước."""
    
    # Logic cũ đã bị loại bỏ, chỉ giữ lại logic mới theo yêu cầu
    if model == "two_steps_resnet":
        return query_by_image_two_steps(img_path, top_k=top_k, content_model="resnet50")
    elif model == "two_steps_clip":
        return query_by_image_two_steps(img_path, top_k=top_k, content_model="clip")
    else:
        # Xử lý trường hợp người dùng vẫn gửi 'clip' hoặc 'resnet50' đơn lẻ
        print(f"Warning: Model '{model}' không được hỗ trợ. Chuyển sang dùng 'two_steps_resnet'.")
        return query_by_image_two_steps(img_path, top_k=top_k, content_model="resnet50")