# # app/services/clip_service.py

# import os
# import faiss
# import json
# import numpy as np
# from PIL import Image
# from facenet_pytorch import MTCNN
# import torch
# from app.core.clip_loader import clip_model, preprocess, DEVICE
# from app.services.base_service import safe_load_image, DATA_DIR, get_actor_movies, get_movie_info

# # Cấu hình CLIP
# ACTOR_INDEX_PATH = os.path.join(DATA_DIR, "actor_index_clip_colab.index")
# ACTOR_LABELS_JSON = os.path.join(DATA_DIR, "actor_labels_clip_colab.json")

# MOVIE_INDEX_PATH = os.path.join(DATA_DIR, "clip_faiss_colab.index")
# MOVIE_LABELS_PATH = os.path.join(DATA_DIR, "clip_faiss_labels_colab.npy")

# # Khởi tạo MTCNN (có thể di chuyển MTCNN lên base_service nếu cả CLIP và ArcFace dùng chung)
# mtcnn = MTCNN(keep_all=True, device=DEVICE)

# # Tải Index và Labels
# try:
#     actor_index = faiss.read_index(ACTOR_INDEX_PATH)
#     with open(ACTOR_LABELS_JSON, "r", encoding="utf-8") as f:
#         actor_labels = json.load(f)
#     print("[CLIP] Actor Index Loaded.")
# except Exception as e:
#     print(f"[ERROR] Could not load CLIP actor index: {e}")
#     actor_index = None
#     actor_labels = []

# # Tải Movie/Content Index và Labels (Dùng cho Bước 1)
# try:
#     MOVIE_INDEX = faiss.read_index(MOVIE_INDEX_PATH)
#     MOVIE_LABELS = np.load(MOVIE_LABELS_PATH, allow_pickle=True)
#     print("[CLIP] Movie/Content Index Loaded.")
# except Exception as e:
#     print(f"[ERROR] Could not load CLIP movie/content index: {e}")
#     MOVIE_INDEX = None
#     MOVIE_LABELS = []

# # Add explicit check/log for CLIP model availability
# if clip_model is None or preprocess is None:
#     print("[ERROR] CLIP model or preprocess is not loaded. Check [clip_loader.py](http://_vscodecontentref_/13) and model files.")

# def extract_clip_feature(pil_img: Image.Image):
#     """Trích xuất vector CLIP 512D (chuẩn hóa L2)."""
#     image = preprocess(pil_img).unsqueeze(0).to(DEVICE)
#     with torch.no_grad():
#         feat = clip_model.encode_image(image)
#         feat = feat / feat.norm(dim=-1, keepdim=True)
#     return feat.cpu().numpy().flatten().astype("float32")

# def detect_face_mtcnn(img_path):
#     """Phát hiện khuôn mặt bằng MTCNN (dùng cho cả CLIP/ResNet)."""
#     img = safe_load_image(img_path)
#     if img is None:
#         return None

#     try:
#         boxes, probs = mtcnn.detect(img)
#         if boxes is None or len(boxes) == 0:
#             return None

#         best_idx = np.argmax(probs)
#         if probs[best_idx] < 0.90: # Ngưỡng phát hiện
#             return None 

#         x1, y1, x2, y2 = map(int, boxes[best_idx])
#         face = img.crop((x1, y1, x2, y2))
#         return face

#     except Exception:
#         return None

# def extract_face_clip_feature(img_path):
#     """
#     Hàm 1: Trích xuất vector đặc trưng CLIP của khuôn mặt phát hiện trong ảnh.
    
#     Trả về: np.ndarray (vector đặc trưng) hoặc None nếu không tìm thấy khuôn mặt.
#     """
#     face = detect_face_mtcnn(img_path)
#     if face is None:
#         # print("[CLIP] No face detected in the input image.")
#         return None
        
#     feat = extract_clip_feature(face)
#     return feat

# def get_all_actor_similarities_clip(input_feat: np.ndarray, top_k_actors=50) -> dict:
#     """
#     Hàm 2: So sánh đặc trưng khuôn mặt đầu vào với TOP K diễn viên gần nhất trong Index Diễn viên CLIP (Global FAISS Search).
    
#     Args:
#         input_feat (np.ndarray): Vector đặc trưng khuôn mặt (1D, 512D).
#         top_k_actors (int): Số lượng diễn viên gần nhất muốn tìm kiếm.
        
#     Trả về: dict: {normalized_actor_name: similarity}
#     """
#     global actor_index, actor_labels
    
#     # *** ĐIỂM SỬA: Kiểm tra biến đã tải (actor_index) ***
#     if actor_index is None or not actor_labels:
#         print("[ERROR] CLIP Actor Index/Labels not loaded for comparison.")
#         return {}
    
#     # Chuyển 1D array thành 2D (1, 512) và chuẩn hóa L2 cho FAISS
#     feat = input_feat.reshape(1, -1)
#     faiss.normalize_L2(feat)
    
#     # *** ĐIỂM SỬA: Sử dụng actor_index.ntotal thay vì ACTOR_INDEX_PATH.ntotal ***
#     k = min(top_k_actors, actor_index.ntotal)
    
#     # Tìm kiếm FAISS 
#     D, I = actor_index.search(feat, k) 
    
#     similarities = {}
#     for dist, index in zip(D[0], I[0]):
#         if index != -1:
#             actor_name = str(actor_labels[index])
#             normalized_actor_name = actor_name.replace("_", " ")
            
#             # Giả định D là Cosine Similarity (IndexFlatIP)
#             sim = dist
            
#             similarities[normalized_actor_name] = float(sim)
            
#     return similarities


# def get_actor_feature(actor_name: str):
#     """Lấy vector đặc trưng CLIP đã lưu của một diễn viên."""
#     global actor_labels, actor_index # Đảm bảo biến toàn cục
#     if actor_index is None:
#         return None
        
#     try:
#         # Tìm index của diễn viên trong actor_labels
#         label_index = actor_labels.index(actor_name)
#         # Vector đặc trưng CLIP đã được lưu trong actor_index
#         feature = actor_index.reconstruct(label_index)
#         return feature
#     except ValueError:
#         return None
#     except Exception as e:
#         print(f"[ERROR] Lỗi lấy đặc trưng diễn viên {actor_name}: {e}")
#         return None


# def query_actor_by_image_clip(img_path, target_actor_name: str):
#     """
#     So sánh ảnh đầu vào (khuôn mặt) với đặc trưng của một diễn viên cụ thể.
#     Trả về: (độ tương đồng, đặc trưng khuôn mặt đã trích)
#     """
#     if actor_index is None:
#         print("[CLIP] Actor Index chưa tải.")
#         return None, None

#     # 1. Trích xuất khuôn mặt từ ảnh đầu vào
#     face = detect_face_mtcnn(img_path)
#     if face is None:
#         return None, None

#     # 2. Trích xuất đặc trưng CLIP từ khuôn mặt ảnh đầu vào
#     feat_input = extract_clip_feature(face)
#     feat_input_normalized = feat_input.reshape(1, -1)
#     faiss.normalize_L2(feat_input_normalized)

#     # 3. Lấy đặc trưng của diễn viên mục tiêu từ Index
#     feat_target = get_actor_feature(target_actor_name)
#     if feat_target is None:
#         return None, feat_input # Trả về None sim nhưng vẫn trả về đặc trưng

#     feat_target_normalized = feat_target.reshape(1, -1)
#     # Không cần chuẩn hóa lại nếu đã chuẩn hóa trước khi lưu, nhưng đảm bảo nhất quán
#     faiss.normalize_L2(feat_target_normalized) 

#     # 4. Tính toán độ tương đồng (Cosine Similarity = Tích vô hướng của vector chuẩn hóa L2)
#     similarity = np.dot(feat_input_normalized, feat_target_normalized.T)[0][0]
    
#     return float(similarity), feat_input # Trả về sim và đặc trưng ảnh đầu vào

# # TẠM THỜI: Thêm hàm giả định cho bước 1 nếu người dùng chọn CLIP
# def extract_clip_feature_content(img_path, top_k=5, threshold=0.25):
#     """
#     Hàm thực hiện Bước 1: Tìm kiếm Frame/Nội dung phim bằng CLIP.
    
#     Args:
#         img_path (str): Đường dẫn đến ảnh đầu vào.
#         top_k (int): Số lượng phim (độc nhất) tối đa muốn trả về.
#         threshold (float): Ngưỡng tương đồng tối thiểu để chấp nhận kết quả.
        
#     Returns:
#         dict: {"movies": list_phim, "message": message}
#     """
#     # Đảm bảo các Index Content đã được tải. Giả định biến MOVIE_INDEX chứa FAISS Index của các frame
#     # và MOVIE_LABELS chứa nhãn của chúng.
#     try:
#         if MOVIE_INDEX is None:
#             return {"movies": [], "message": "CLIP Content Index chưa tải."}
#     except NameError:
#         print("[ERROR] Biến MOVIE_INDEX/MOVIE_LABELS chưa được định nghĩa. Xin hãy kiểm tra lại.")
#         return {"movies": [], "message": "CLIP Content Index chưa được định nghĩa."}

#     # 1. Tải và tiền xử lý ảnh
#     img = safe_load_image(img_path)
#     if img is None:
#         return {"movies": [], "message": "Không thể tải hoặc xử lý ảnh đầu vào."}
    
#     image_tensor = preprocess(img).unsqueeze(0).to(DEVICE)

#     # 2. Trích xuất đặc trưng của toàn bộ ảnh (Content Feature)
#     with torch.no_grad():
#         image_features = clip_model.encode_image(image_tensor)
        
#     # Chuẩn bị vector cho FAISS
#     feat = image_features.cpu().numpy().astype('float32')
#     feat = feat.reshape(1, -1)
#     faiss.normalize_L2(feat)
    
#     # 3. Truy vấn FAISS (Tăng số lượng truy vấn ban đầu để lọc tốt hơn)
#     # Tăng k lên 5 lần để đảm bảo có đủ frame từ các phim khác nhau
#     D, I = MOVIE_INDEX.search(feat, top_k * 5) 
    
#     # 4. Xử lý và lọc kết quả trùng lặp (nhiều frame từ 1 phim)
#     results = {} 
    
#     for sim, label_idx in zip(D[0], I[0]):
#         if sim < threshold:
#             continue
            
#         # Lấy nhãn (tên file feature/frame)
#         raw_label = str(MOVIE_LABELS[label_idx]) # hoặc CONTENT_LABELS
        
#         # --- LOGIC MỚI LẤY FULL KEY CỦA PHIM (ví dụ: Cho_Em_Gan_Anh_Them_Chut_Nua) ---
#         cleaned_label = raw_label
        
#         # 1. Loại bỏ phần mở rộng file (ví dụ: .npy, .tmp)
#         if '.' in cleaned_label:
#             cleaned_label = cleaned_label.rsplit('.', 1)[0]
        
#         # 2. Loại bỏ chỉ số frame/clip (ví dụ: _1234, _Frame001) ở cuối
#         # Giả định phần chỉ số này nằm sau dấu gạch dưới cuối cùng và không chứa director ('by')
#         parts = cleaned_label.rsplit("_", 1)
        
#         if len(parts) > 1 and parts[1] and not parts[1].startswith('by'):
#             # Nếu phần sau dấu '_' cuối cùng là số, hoặc bắt đầu bằng 'Frame'/'Clip', ta giả định nó là index và loại bỏ.
#             if parts[1].isdigit() or parts[1].startswith('Frame') or parts[1].startswith('Clip'):
#                 cleaned_label = parts[0]

#         if cleaned_label not in results:
#             # Giả định get_movie_info(title) trả về dict thông tin phim
#             info = get_movie_info(cleaned_label)
#             if info:
#                 # Thêm độ tương đồng (similarity) vào thông tin phim
#                 info["similarity"] = float(sim)
#                 results[cleaned_label] = info
                
#             # Đã đủ số lượng top_k
#             if len(results) >= top_k:
#                 break


#     if not results:
#         print(f"[CLIP_CONTENT] Search found 0 results. Max similarity: {D[0][0]:.4f}.")
#         return {"movies": [], "message": f"Không tìm thấy nội dung phim nào (Độ tương đồng tối đa: {D[0][0]:.2f})"}

#     # Trả về danh sách phim duy nhất được tìm thấy
#     return {
#         "movies": list(results.values()), # list các dict phim
#         "message": f"Tìm thấy {len(results)} phim liên quan bằng CLIP Content Search."
#     }