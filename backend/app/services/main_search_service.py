# app/services/main_search_service.py

# Import các hàm từ các service 
from app.services.clip_service import query_by_image_clip

# from app.services.text_search_service import query_by_text
# from app.services.chatbot_service import query_by_text_chatbot
# from app.services.base_service import query_by_keyword

from app.services.resnet_service import query_by_image_resnet50 


def query_by_image(img_path, model="clip", top_k=5):
    """
    Hàm tổng hợp cho truy vấn ảnh.
    model: 'clip', 'arcface' (hoặc 'resnet50').
    """
    
    if model == "resnet50":
        return query_by_image_resnet50(img_path, top_k=top_k) 

    # Mặc định là CLIP
    return query_by_image_clip(img_path, top_k=top_k)

# Các hàm khác có thể được import trực tiếp từ file text_search_service


# (Các hàm khác như query_by_keyword và suggest_popular_movies giữ nguyên hoặc chuyển sang base_service)