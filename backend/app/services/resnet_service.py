# app/services/resnet_service.py

import os
import faiss
import json
import numpy as np
from PIL import Image
import keras
from keras.utils import load_img, img_to_array 
from keras.models import load_model, Model
from keras.applications.resnet50 import preprocess_input

from app.services.base_service import DATA_DIR, get_actor_movies
import logging

logger = logging.getLogger("app.resnet")


# Nếu không có base_service, bạn cần định nghĩa lại get_movie_info và DATA_DIR ở đây.


# =========================
# CONFIG - MOVIE CONTENT SEARCH (FRAME RETRIEVAL)
# =========================
# Tên file model ResNet50 dùng cho trích xuất đặc trưng nội dung
# MODEL_FILENAME = "resnet50_feature_extractor_cosine.h5" 
MODEL_FILENAME = "resnet50_feature_extractor_2.h5"

# File Index và Labels riêng cho đặc trưng NỘI DUNG (FRAME)
# CONTENT_INDEX_FILENAME = "movie_resnet50_content.index" 
# CONTENT_LABELS_FILENAME = "movie_resnet50_content_labels.npy"

CONTENT_INDEX_FILENAME = "actor_resnet50_face.index" 
CONTENT_LABELS_FILENAME = "actor_resnet50_face_labels.npy"

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

# Định nghĩa đường dẫn file
MODEL_PATH = os.path.join(DATA_DIR, MODEL_FILENAME)
CONTENT_INDEX_PATH = os.path.join(DATA_DIR, CONTENT_INDEX_FILENAME)
# Cần dùng đường dẫn .npy mới
CONTENT_LABELS_NPY = os.path.join(DATA_DIR, CONTENT_LABELS_FILENAME)


# Tải và định nghĩa mô hình FEATURE_EXTRACTOR_MODEL
try:
    base_model = load_model(MODEL_PATH)
    
    feature_extractor_model = Model(inputs=base_model.input, outputs=base_model.layers[-2].output)
    logger.info("[ResNet] Feature Extractor Model Loaded.")
except Exception as e:
    logger.error(f"[ERROR] Could not load ResNet feature extractor model from {MODEL_PATH}: {e}")
    feature_extractor_model = None


# Tải Index và Labels
CONTENT_INDEX = None
CONTENT_LABELS = []
try:
    if os.path.exists(CONTENT_INDEX_PATH):
        CONTENT_INDEX = faiss.read_index(CONTENT_INDEX_PATH)
        
        # --- LOGIC TẢI FILE LABELS (.NPY) ---
        if CONTENT_LABELS_FILENAME.endswith('.npy'):
             # Tải file labels NumPy
             CONTENT_LABELS = np.load(CONTENT_LABELS_NPY) 
        elif CONTENT_LABELS_FILENAME.endswith('.json'):
             # Logic cũ (giữ lại nếu cần cho mục đích debug)
             with open(CONTENT_LABELS_NPY, "r", encoding="utf-8") as f:
                 CONTENT_LABELS = json.load(f)
        
        logger.info(f"[ResNet] Actor Index Loaded with {CONTENT_INDEX.ntotal} vectors and {len(CONTENT_LABELS)} labels.")
    else:
        logger.warning(f"[ResNet] Actor Index file not found at {CONTENT_INDEX_PATH}")

except Exception as e:
    logger.error(f"[ERROR] Could not load ResNet actor index: {e}")
    CONTENT_INDEX = None
    CONTENT_LABELS = []


# =========================
# HÀM TRÍCH XUẤT VÀ TRUY VẤN
# =========================

def extract_resnet_feature(img_path):
    """Trích xuất vector đặc trưng từ ảnh đầu vào bằng ResNet50."""
    
    if feature_extractor_model is None:
        logger.error("feature_extractor_model is not loaded.")
        return None

    try:
        # 1. Tiền xử lý ảnh (Ảnh phải là 224x224)
        img = load_img(img_path, target_size=(224, 224)) 
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)

        # 2. Trích xuất bản đồ đặc trưng (Feature Map)
        # Kết quả có shape là (1, 7, 7, 2048)
        feat_map = feature_extractor_model.predict(img_array, verbose=0)[0] 
        
        # 3. ÁP DỤNG GLOBAL AVERAGE POOLING (Fix Lỗi Assertion)
        # Tính giá trị trung bình trên trục chiều cao (axis 0) và chiều rộng (axis 1)
        # để chuyển tensor (7, 7, 2048) thành vector (2048,)
        feat = np.mean(feat_map, axis=(0, 1)) 

        # Vector đặc trưng cuối cùng là 2048D
        return feat

    except Exception as e:
        logger.error(f"Lỗi trích xuất đặc trưng ResNet50: {e}")
        return None

def query_by_image_resnet50(img_path, top_k=5, threshold=0.30):
    """
    Truy vấn diễn viên bằng đặc trưng ResNet50 (Actor Recognition).
    """
    
    if CONTENT_INDEX is None:
        return {"actor": None, "movies": [], "message": "ResNet50 Actor Index chưa tải."}

    # 1. Trích xuất đặc trưng
    feat = extract_resnet_feature(img_path)
    if feat is None:
        return {"actor": None, "movies": [], "message": "Không thể trích xuất đặc trưng ResNet50."}

    # Chuẩn bị vector cho FAISS
    feat = feat.reshape(1, -1)
    faiss.normalize_L2(feat)
    
    # 3. Truy vấn FAISS (Chỉ tìm k=1 vì chỉ cần match 1 diễn viên)
    D, I = CONTENT_INDEX.search(feat, 1) 
    
    best_sim = D[0][0]
    best_idx = I[0][0]
    
    # 4. Lọc kết quả theo ngưỡng
    if best_sim < threshold:
        logger.warning(
            f"ResNet50 Actor search found 0 results. Max similarity: {best_sim:.4f}. Current threshold: {threshold}. "
            f"Diễn viên không được nhận dạng hoặc ngưỡng quá cao."
        )
        return {"actor": None, "movies": [], "message": f"Không tìm thấy diễn viên nào (Độ tương đồng tối đa: {best_sim:.2f})"}
    
    # Lấy tên diễn viên từ labels
    raw_actor_name = str(CONTENT_LABELS[best_idx])
    actor_name = raw_actor_name.replace("_", " ")
    
    # 5. Lấy danh sách phim của diễn viên đó
    # KHẮC PHỤC LỖI TYPEERROR: Gọi hàm mà không có tham số top_k
    full_movie_list = get_actor_movies(actor_name)
    
    # Giới hạn số lượng kết quả bằng cách cắt lát (slicing)
    movie_list = full_movie_list[:top_k]

    logger.info(f"ResNet50 recognized actor: {actor_name} with similarity: {best_sim:.4f}. Movies found: {len(movie_list)}")
    
    return {
        "actor": actor_name, 
        "movies": movie_list, # Trả về danh sách đã cắt lát
        "similarity": float(best_sim), # Thêm độ tương đồng
        "message": f"Diễn viên được nhận diện: {actor_name} (Độ tương đồng: {best_sim:.2f})"
    }