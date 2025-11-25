# app/services/main_search_service.py

# Import các hàm từ các service 

# from app.services.text_search_service import query_by_text
# from app.services.chatbot_service import query_by_text_chatbot
# from app.services.base_service import query_by_keyword

from app.services.clip_service import query_actor_by_image_clip, extract_clip_feature_content
from app.services.resnet_service import query_by_image_resnet50_content
from app.services.base_service import get_all_actors_in_movie, safe_load_image

# def query_by_image(img_path, model="clip", top_k=5):
#     """
#     Hàm tổng hợp cho truy vấn ảnh.
#     model: 'clip', 'arcface' (hoặc 'resnet50').
#     """
    
#     if model == "resnet50":
#         return query_by_image_resnet50(img_path, top_k=top_k) 

#     # Mặc định là CLIP
#     return query_by_image_clip(img_path, top_k=top_k)

# Các hàm khác có thể được import trực tiếp từ file text_search_service


# (Các hàm khác như query_by_keyword và suggest_popular_movies giữ nguyên hoặc chuyển sang base_service)

def get_content_search_results(img_path, content_model, top_k):
    """
    Hàm wrapper để gọi đúng logic tìm kiếm content/frame (Bước 1)
    dựa trên model đã chọn.
    """
    if content_model == "resnet50":
        # Hàm này đã được định nghĩa trong resnet_service.py
        return query_by_image_resnet50_content(img_path, top_k=top_k)
    elif content_model == "clip":
        # Hàm này đã được triển khai trong clip_service.py
        return extract_clip_feature_content(img_path, top_k=top_k)
    else:
        # Xử lý trường hợp model không hợp lệ cho bước 1
        return {"movies": [], "message": f"Model content '{content_model}' không hợp lệ."}

def query_by_image_two_steps(img_path, top_k=5, content_model="resnet50", actor_threshold=0.35, content_threshold=0.25):
    """
    Thực hiện logic tìm kiếm 2 bước: 
    1. Tìm Content/Frame (dùng content_model: resnet50/clip)
    2. Tìm Diễn viên (luôn dùng CLIP Actor Index)
    """
    # 1. BƯỚC 1: Tìm Content/Frame
    # (Đây là dòng gây lỗi trong traceback nếu hàm này chưa được định nghĩa)
    content_results = get_content_search_results(img_path, content_model, top_k) 
    
    movie_list = content_results.get("movies", [])
    if not movie_list:
        return {
            "status": "success",
            "actor": None,
            "movies": [],
            "actor_similarities": [],
            "message": content_results.get("message", "Không tìm thấy phim liên quan.")
        }
    # 2. BƯỚC 2: So sánh đặc trưng khuôn mặt với diễn viên của TẤT CẢ các phim vừa tìm được
    actor_similarities = {}
    
    # Lấy khuôn mặt từ ảnh đầu vào (Cần hàm detect_face_mtcnn trong clip_service/base_service)
    # Giả định khuôn mặt được trích xuất thành công trong clip_service
    face_feature = None

    # Lặp qua tất cả các phim được tìm thấy
    all_actors_to_check = set()
    for movie in movie_list:
        title = movie.get("original_title") or movie.get("title")
        print(f"[INFO] Xử lý phim: {title}")
        
        # Lấy danh sách diễn viên tham gia trong phim này (Cần hàm này trong base_service.py)
        # Giả định get_all_actors_in_movie(title) trả về list tên diễn viên
        actor_names_in_movie = get_all_actors_in_movie(title) 
        all_actors_to_check.update(actor_names_in_movie)
        print(f"[INFO] Tìm thấy {len(actor_names_in_movie)} diễn viên trong phim '{title}'.")

    # So sánh với từng diễn viên đã được đề xuất
    for actor_name in all_actors_to_check:
        
        # Gọi hàm mới trong clip_service để so sánh ảnh đầu vào với đặc trưng diễn viên
        # Hàm này trả về độ tương đồng khuôn mặt (similarity score)
        similarity, face_feature = query_actor_by_image_clip(img_path, target_actor_name=actor_name)
        print(f"[DEBUG] So sánh với diễn viên '{actor_name}': similarity = {similarity}")
        
        # Chỉ lưu nếu có độ tương đồng đáng kể
        if similarity is not None and similarity > 0.40: # Ngưỡng tối thiểu 0.4
            actor_similarities[actor_name] = similarity
            
        # Nếu so sánh lần đầu, lưu lại đặc trưng khuôn mặt để tránh trích xuất lại
        if face_feature is not None and 'face_feature' not in content_results:
            content_results['face_feature'] = face_feature


    # Sắp xếp diễn viên theo độ tương đồng giảm dần
    sorted_actors = sorted(actor_similarities.items(), key=lambda item: item[1], reverse=True)


    best_actor = sorted_actors[0][0] if sorted_actors else None
    
    # Chuẩn bị kết quả cuối cùng
    return {
        "status": "success",
        "actor": best_actor, # Diễn viên có độ tương đồng cao nhất
        "movies": movie_list, # Danh sách phim tìm được từ frame
        "actor_similarities": sorted_actors, # Độ tương đồng của các diễn viên (tên, sim)
        "message": f"Tìm thấy {len(movie_list)} phim liên quan. Diễn viên tiềm năng: {best_actor} (Sim: {sorted_actors[0][1]:.2f})" if best_actor else "Tìm thấy phim, nhưng không nhận dạng được diễn viên rõ ràng."
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