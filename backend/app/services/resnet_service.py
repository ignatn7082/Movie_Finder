# import os
# import faiss
# import numpy as np
# import json
# from PIL import Image
# from app.services.base_service import DATA_DIR, safe_load_image, get_movie_info 
# from tensorflow.keras.models import load_model, Model
# from tensorflow.keras.applications.resnet50 import preprocess_input
# from tensorflow.keras.preprocessing import image

# # Tải các hàm dùng chung từ base_service

# # NOTE: Đã thay get_actor_movies bằng get_movie_info

# # Giả sử file index và model được đặt trong thư mục `data` của project API
# MODEL_FILENAME = "resnet50_feature_extractor_cosine.h5"
# INDEX_FILENAME = "resnet_faiss_cosine.index"
# LABELS_FILENAME = "train_labels_cosine.npy" # Nhãn lúc này là TÊN PHIM/ID PHIM

# RESNET_MODEL_PATH = os.path.join(DATA_DIR, MODEL_FILENAME)
# RESNET_INDEX_PATH = os.path.join(DATA_DIR, INDEX_FILENAME)
# RESNET_LABELS_PATH = os.path.join(DATA_DIR, LABELS_FILENAME)

# # Khởi tạo biến toàn cục
# RESNET_MODEL: Model = None
# RESNET_INDEX = None
# RESNET_LABELS = []

# # =========================
# # 1. Tải Model và Index
# # =========================

# def load_resnet50_resources():
#     """Tải mô hình ResNet50 và chỉ mục FAISS đã được xây dựng."""
#     global RESNET_MODEL, RESNET_INDEX, RESNET_LABELS
    
#     # 1. Tải Model (Keras/TensorFlow)
#     if os.path.exists(RESNET_MODEL_PATH):
#         try:
#             print("[RESNET] Loading Keras ResNet50 model...")
#             RESNET_MODEL = load_model(RESNET_MODEL_PATH, compile=False)
#             print("[RESNET] Model Loaded.")
#         except Exception as e:
#             print(f"[ERROR] Cannot load Keras model from {RESNET_MODEL_PATH}: {e}")
#             RESNET_MODEL = None
    
#     # 2. Tải Index FAISS
#     if os.path.exists(RESNET_INDEX_PATH):
#         try:
#             print("[RESNET] Loading FAISS index...")
#             RESNET_INDEX = faiss.read_index(RESNET_INDEX_PATH)
#             print(f"[RESNET] Index Loaded with {RESNET_INDEX.ntotal} vectors.")
#         except Exception as e:
#             print(f"[ERROR] Cannot load FAISS index from {RESNET_INDEX_PATH}: {e}")
#             RESNET_INDEX = None
            
#     # 3. Tải Labels
#     if os.path.exists(RESNET_LABELS_PATH):
#         try:
#             print("[RESNET] Loading labels...")
#             # Nhãn sẽ là tên phim/ID phim
#             RESNET_LABELS = np.load(RESNET_LABELS_PATH, allow_pickle=True).tolist()
#         except Exception as e:
#             print(f"[ERROR] Cannot load labels from {RESNET_LABELS_PATH}: {e}")
#             RESNET_LABELS = []

# # Tải tài nguyên khi khởi động
# load_resnet50_resources()

# # =========================
# # 2. Hàm Trích xuất Đặc trưng
# # =========================

# def extract_resnet50_feature(img_path, target_size=(224, 224)):
#     """Trích xuất vector 2048 chiều (L2 normalized) từ ảnh frame phim."""
#     if RESNET_MODEL is None:
#         return None
        
#     try:
#         # Load ảnh frame
#         img = image.load_img(img_path, target_size=target_size)
        
#         # Tiền xử lý chuẩn ResNet50
#         x = image.img_to_array(img)
#         x = np.expand_dims(x, axis=0)
#         x = preprocess_input(x)
        
#         # Dự đoán
#         feat = RESNET_MODEL.predict(x, verbose=0)
#         feat = feat.flatten().astype("float32").reshape(1, -1)
        
#         # Chuẩn hóa L2 (Cần thiết vì index là IndexFlatIP - Cosine Similarity)
#         faiss.normalize_L2(feat)
        
#         return feat[0]
        
#     except Exception as e:
#         print(f"[ERROR] Failed to extract ResNet50 feature for {img_path}: {e}")
#         return None

# # =========================
# # 3. Hàm Truy vấn Nội dung Phim
# # =========================

# def query_by_image_resnet50(img_path, top_k=5, threshold=0.75):
#     """
#     Truy vấn phim tương đồng bằng ảnh frame, sử dụng ResNet50 và FAISS Cosine.
#     Trả về thông tin chi tiết của phim có frame khớp nhất.
#     """
#     if RESNET_INDEX is None or not RESNET_LABELS:
#         return {"movie_title": None, "message": "ResNet50 Index chưa sẵn sàng."}

#     # 1. Trích xuất đặc trưng
#     feat = extract_resnet50_feature(img_path)
#     if feat is None:
#         return {"movie_title": None, "message": "Lỗi trích xuất đặc trưng ResNet50"}

#     feat = feat.reshape(1, -1)

#     # 2. Truy vấn FAISS (IndexFlatIP)
#     D, I = RESNET_INDEX.search(feat, top_k)
#     best_sim = float(D[0][0])
#     # Nhãn tốt nhất là nhãn của frame, mà frame này thuộc một bộ phim
#     best_frame_label = RESNET_LABELS[I[0][0]] 

#     # 3. Kiểm tra ngưỡng
#     if best_sim < threshold: 
#         return {"movie_title": None, "message": f"Không tìm thấy nội dung tương đồng (Độ tương đồng: {best_sim:.2f} < {threshold})"}

#     # 4. Lấy thông tin phim từ nhãn (dùng hàm get_movie_info từ base_service)
#     # Giả định best_frame_label là tên phim hoặc ID phim
#     movie_info = get_movie_info(best_frame_label)
    
#     # Thêm độ tương đồng vào kết quả
#     movie_info["similarity"] = best_sim
#     movie_info["match_type"] = "resnet_frame_content"
    
#     # Để trả về nhiều kết quả, ta có thể lặp qua top_k, nhưng ở đây ta chỉ lấy kết quả tốt nhất
#     return [movie_info] # Trả về dưới dạng list (tương tự như các hàm query khác)

# app/services/resnet_service.py

import os
import faiss
import numpy as np
from PIL import Image
import keras
from keras.utils import load_img, img_to_array 
from keras.models import load_model, Model
from keras.applications.resnet50 import preprocess_input
# Sửa lỗi Pylance/TensorFlow: Sử dụng load_img và img_to_array từ keras.utils
# from tensorflow.keras.utils import load_img, img_to_array
# from tensorflow.keras.models import load_model, Model
# from tensorflow.keras.applications.resnet50 import preprocess_input

# Import các hàm dùng chung (Cần đảm bảo get_movie_info và DATA_DIR được định nghĩa)
# Giả định các hàm này được định nghĩa trong app/services/base_service.py hoặc file tương đương
from app.services.base_service import DATA_DIR, get_movie_info 
# Nếu không có base_service, bạn cần định nghĩa lại get_movie_info và DATA_DIR ở đây.


# =========================
# CONFIG - MOVIE CONTENT SEARCH (FRAME RETRIEVAL)
# =========================
# Tên file model ResNet50 dùng cho trích xuất đặc trưng nội dung
MODEL_FILENAME = "resnet50_content_extractor.h5" 

# File Index và Labels riêng cho đặc trưng NỘI DUNG (FRAME)
CONTENT_INDEX_FILENAME = "movie_resnet50_content.index" 
CONTENT_LABELS_FILENAME = "movie_resnet50_content_labels.npy"

RESNET_MODEL_PATH = os.path.join(DATA_DIR, MODEL_FILENAME)
CONTENT_INDEX_PATH = os.path.join(DATA_DIR, CONTENT_INDEX_FILENAME)
CONTENT_LABELS_PATH = os.path.join(DATA_DIR, CONTENT_LABELS_FILENAME)

# Khởi tạo biến toàn cục
RESNET_MODEL: Model = None
CONTENT_INDEX = None
CONTENT_LABELS = []

# =========================
# 1. Tải Model và Index
# =========================

def load_resnet50_content_resources():
    """Tải mô hình ResNet50 và chỉ mục FAISS nội dung phim."""
    global RESNET_MODEL, CONTENT_INDEX, CONTENT_LABELS
    
    # Tải Model
    if RESNET_MODEL is None and os.path.exists(RESNET_MODEL_PATH):
        try:
            print("[RESNET_CONTENT] Loading Keras ResNet50 model...")
            RESNET_MODEL = load_model(RESNET_MODEL_PATH, compile=False) 
        except Exception as e:
            print(f"[ERROR] Cannot load Keras model from {RESNET_MODEL_PATH}: {e}")
            RESNET_MODEL = None
    
    # Tải Index FAISS
    if os.path.exists(CONTENT_INDEX_PATH):
        try:
            print("[RESNET_CONTENT] Loading FAISS CONTENT index...")
            CONTENT_INDEX = faiss.read_index(CONTENT_INDEX_PATH)
        except Exception as e:
            print(f"[ERROR] Cannot load FAISS CONTENT index: {e}")
            CONTENT_INDEX = None
            
    # Tải Labels
    if os.path.exists(CONTENT_LABELS_PATH):
        try:
            print("[RESNET_CONTENT] Loading CONTENT labels...")
            CONTENT_LABELS = np.load(CONTENT_LABELS_PATH, allow_pickle=True).tolist() 
        except Exception as e:
            print(f"[ERROR] Cannot load CONTENT labels: {e}")
            CONTENT_LABELS = []

# Tải tài nguyên khi khởi động
load_resnet50_content_resources()

# =========================
# 2. Hàm Trích xuất Đặc trưng Nội dung
# =========================

def extract_resnet50_feature(pil_img: Image.Image, target_size=(224, 224)):
    """Trích xuất vector 2048 chiều từ ảnh PIL nội dung phim."""
    if RESNET_MODEL is None:
        return None
        
    try:
        # Resize và chuyển sang NumPy array
        img_resized = pil_img.resize(target_size, Image.LANCZOS)
        x = img_to_array(img_resized)
        x = np.expand_dims(x, axis=0)
        
        # Tiền xử lý chuẩn ResNet50
        x = preprocess_input(x)
        
        # Dự đoán
        feat = RESNET_MODEL.predict(x, verbose=0)
        feat = feat.flatten().astype("float32").reshape(1, -1)
        
        # Chuẩn hóa L2 (cho Cosine Similarity)
        faiss.normalize_L2(feat)
        
        return feat[0]
        
    except Exception as e:
        print(f"[ERROR] Failed to extract ResNet50 CONTENT feature: {e}")
        return None
        
def safe_load_image(path):
    """Tải ảnh an toàn, đảm bảo kích thước không quá lớn."""
    MAX_SIZE = 1024
    try:
        img = Image.open(path).convert("RGB")
    except Exception:
        return None

    w, h = img.size
    if max(w, h) > MAX_SIZE:
        scale = MAX_SIZE / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    return img

# =========================
# 3. Hàm Truy vấn Nội dung (Frame Retrieval)
# =========================

def query_by_image_resnet50(img_path, top_k=5, threshold=0.65):
    """
    Truy vấn phim bằng ảnh nội dung/frame, sử dụng ResNet50 Feature Extractor.
    """
    if CONTENT_INDEX is None or not CONTENT_LABELS:
        return [{"title": "ResNet50 Content Index chưa sẵn sàng.", "poster": None, "similarity": 0.0}]

    # 1. Load ảnh
    img = safe_load_image(img_path)
    if img is None:
        return [{"title": "Lỗi tải ảnh hoặc ảnh không hợp lệ.", "poster": None, "similarity": 0.0}]
        
    # 2. Trích xuất đặc trưng
    feat = extract_resnet50_feature(img)
    if feat is None:
        return [{"title": "Lỗi trích xuất đặc trưng ResNet50.", "poster": None, "similarity": 0.0}]

    feat = feat.reshape(1, -1)

    # 3. Truy vấn FAISS
    D, I = CONTENT_INDEX.search(feat, top_k * 5) 
    
    # 4. Xử lý và lọc kết quả trùng lặp (nhiều frame từ 1 phim)
    results = {} 
    
    for sim, label in zip(D[0], I[0]):
        if sim < threshold:
            continue
            
        # Nhãn frame có thể là "Tên Phim_FrameXX". Cần lấy tên phim gốc.
        movie_title_raw = str(CONTENT_LABELS[label]).split("_")[0].replace("_", " ") 

        if movie_title_raw not in results:
            info = get_movie_info(movie_title_raw)
            if info:
                info["similarity"] = float(sim)
                results[movie_title_raw] = info
                
            if len(results) >= top_k:
                break
                
    final_results = list(results.values())
    final_results = (
        final_results.replace(".npy.tmp", "")
                  .replace(".npy", "")
                  .replace(".tmp", "")
    )
    
    if not final_results:
        return [{"title": f"Không tìm thấy phim (Độ tương đồng < {threshold})", "poster": None, "similarity": 0.0}]

    return final_results