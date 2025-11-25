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

from app.services.base_service import DATA_DIR, get_actor_movies, get_movie_info

# =========================
# CONFIG - MODEL & INDICES
# =========================
MODEL_FILENAME = "resnet50_feature_extractor.h5"

# Config cho Content/Frame
CONTENT_INDEX_FILENAME = "resnet_faiss_cosine.index" 
CONTENT_LABELS_FILENAME = "train_labels_cosine.npy"

# Config cho Actor Recognition (NEW)
ACTOR_INDEX_FILENAME = "actor_resnet50_face_3.index" 
ACTOR_LABELS_FILENAME = "actor_resnet50_face_labels_3.npy"

# --- Define Global Paths ---
RESNET_MODEL_PATH = os.path.join(DATA_DIR, MODEL_FILENAME)

CONTENT_INDEX_PATH = os.path.join(DATA_DIR, CONTENT_INDEX_FILENAME)
CONTENT_LABELS_PATH = os.path.join(DATA_DIR, CONTENT_LABELS_FILENAME)

ACTOR_INDEX_PATH = os.path.join(DATA_DIR, ACTOR_INDEX_FILENAME)
ACTOR_LABELS_PATH = os.path.join(DATA_DIR, ACTOR_LABELS_FILENAME)

# Khởi tạo biến toàn cục
FEATURE_EXTRACTOR_MODEL: Model = None 
CONTENT_INDEX = None
CONTENT_LABELS = []

# Khởi tạo biến toàn cục cho Actor (NEW)
ACTOR_INDEX = None
ACTOR_LABELS = []

# =========================
# 1. Tải Model và Index
# =========================

def load_resnet50_resources():
    """Tải mô hình ResNet50 và chỉ mục FAISS nội dung phim VÀ diễn viên."""
    global FEATURE_EXTRACTOR_MODEL, CONTENT_INDEX, CONTENT_LABELS, ACTOR_INDEX, ACTOR_LABELS
    
    # 1. Tải Model và tạo Feature Extractor
    if FEATURE_EXTRACTOR_MODEL is None and os.path.exists(RESNET_MODEL_PATH):
        try:
            print(" Loading Keras ResNet50 model and creating feature extractor...")
            base_model = load_model(RESNET_MODEL_PATH, compile=False) 
            # Output là layer trước Global Average Pooling
            FEATURE_EXTRACTOR_MODEL = Model(inputs=base_model.input, outputs=base_model.layers[-2].output)
            print("[ResNet] Feature Extractor Model Loaded.")
            
        except Exception as e:
            print(f"[ERROR] Could not load ResNet feature extractor model from {RESNET_MODEL_PATH}: {e}")
            FEATURE_EXTRACTOR_MODEL = None
            return 
    
    # 2. Tải Index/Labels cho CONTENT
    if os.path.exists(CONTENT_INDEX_PATH):
        try:
            print(" Loading FAISS CONTENT index...")
            CONTENT_INDEX = faiss.read_index(CONTENT_INDEX_PATH)
            
            if os.path.exists(CONTENT_LABELS_PATH):
                print("[RESNET_CONTENT] Loading CONTENT labels...")
                if CONTENT_LABELS_FILENAME.endswith('.npy'):
                    CONTENT_LABELS = np.load(CONTENT_LABELS_PATH, allow_pickle=True).tolist()
                elif CONTENT_LABELS_FILENAME.endswith('.json'):
                    with open(CONTENT_LABELS_PATH, "r", encoding="utf-8") as f:
                        CONTENT_LABELS = json.load(f)
                
                print(f"[ResNet] Content Index Loaded with {CONTENT_INDEX.ntotal} vectors and {len(CONTENT_LABELS)} labels.")
            else:
                 print(f"[WARNING] Content labels file not found at {CONTENT_LABELS_PATH}")

        except Exception as e:
            print(f"[ERROR] Cannot load FAISS CONTENT index or labels: {e}")
            CONTENT_INDEX = None
            CONTENT_LABELS = []
    else:
        print(f"[WARNING] ResNet Content Index file not found at {CONTENT_INDEX_PATH}")


    # 3. Tải Index/Labels cho DIỄN VIÊN (NEW)
    if os.path.exists(ACTOR_INDEX_PATH):
        try:
            print(" Loading FAISS ACTOR index...")
            ACTOR_INDEX = faiss.read_index(ACTOR_INDEX_PATH)
            
            if os.path.exists(ACTOR_LABELS_PATH):
                print("[RESNET_ACTOR] Loading ACTOR labels...")
                # Giả định labels được lưu trong file .npy
                ACTOR_LABELS = np.load(ACTOR_LABELS_PATH, allow_pickle=True).tolist()
                print(f"[ResNet] Actor Index Loaded with {ACTOR_INDEX.ntotal} vectors and {len(ACTOR_LABELS)} labels.")
            else:
                 print(f"[WARNING] ResNet Actor labels file not found at {ACTOR_LABELS_PATH}")

        except Exception as e:
            print(f"[ERROR] Cannot load FAISS ACTOR index or labels: {e}")
            ACTOR_INDEX = None
            ACTOR_LABELS = []
    else:
        print(f"[WARNING] ResNet Actor Index file not found at {ACTOR_INDEX_PATH}")

# Tải tài nguyên khi khởi động
load_resnet50_resources()

# =========================
# 2. Hàm Trích xuất Đặc trưng Nội dung
# =========================

def extract_resnet_feature(img_path):
    """Trích xuất vector đặc trưng từ ảnh đầu vào bằng ResNet50."""
    
    global FEATURE_EXTRACTOR_MODEL
    
    if FEATURE_EXTRACTOR_MODEL is None:
        print("[ERROR] FEATURE_EXTRACTOR_MODEL is not loaded. Cannot extract feature.")
        return None

    try:
        # Tiền xử lý ảnh (target_size=(224, 224))
        img = load_img(img_path, target_size=(224, 224)) 
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)

        # Trích xuất bản đồ đặc trưng 
        feat_map = FEATURE_EXTRACTOR_MODEL.predict(img_array, verbose=0)[0] 
        
        # ÁP DỤNG GLOBAL AVERAGE POOLING
        feat = np.mean(feat_map, axis=(0, 1)) 

        return feat

    except Exception as e:
        print(f"Lỗi trích xuất đặc trưng ResNet50: {e}")
        return None

# =========================
# 3. Hàm Truy vấn Diễn viên (NEW)
# =========================

def query_by_image_resnet50(img_path, top_k=5, threshold=0.30):
    """
    Truy vấn diễn viên bằng đặc trưng ResNet50 (Actor Recognition).
    Sử dụng ResNet Actor Index.
    """
    
    global ACTOR_INDEX, ACTOR_LABELS
    
    if ACTOR_INDEX is None:
        return {"status": "error", "actor": None, "movies": [], "similarity": 0.0, "message": "ResNet50 Actor Index chưa tải."}

    # 1. Trích xuất đặc trưng
    feat = extract_resnet_feature(img_path)
    if feat is None:
        return {"status": "error", "actor": None, "movies": [], "similarity": 0.0, "message": "Không thể trích xuất đặc trưng ResNet50."}

    # Chuẩn bị vector cho FAISS
    feat = feat.reshape(1, -1)
    faiss.normalize_L2(feat) # Chuẩn hóa L2 cho tìm kiếm Cosine Similarity
    
    # 2. Truy vấn FAISS (Chỉ tìm k=1)
    D, I = ACTOR_INDEX.search(feat, 1) 
    
    best_dist = D[0][0] # Kết quả là Cosine Distance
    best_idx = I[0][0]
    
    # Tính độ tương đồng (giả định Cosine Similarity = 1 - Cosine Distance)
    best_sim = 1.0 - best_dist 
    
    # 3. Lọc kết quả theo ngưỡng (threshold là độ tương đồng TỐI THIỂU)
    if best_sim < threshold:
        print(
            f"[WARNING] ResNet50 Actor search found 0 results. Max similarity: {best_sim:.4f}. Current threshold: {threshold}. "
            f"Diễn viên không được nhận dạng hoặc ngưỡng quá cao."
        )
        return {"status": "success", "actor": None, "movies": [], "similarity": float(best_sim), "message": f"Không tìm thấy diễn viên nào (Độ tương đồng tối đa: {best_sim:.2f})"}
    
    # 4. Lấy tên diễn viên từ labels
    raw_actor_name = str(ACTOR_LABELS[best_idx])
    actor_name = raw_actor_name.replace("_", " ") # Xử lý tên diễn viên
    
    # 5. Lấy danh sách phim của diễn viên đó
    full_movie_list = get_actor_movies(actor_name)
    movie_list = full_movie_list[:top_k]

    print(f"ResNet50 recognized actor: {actor_name} with similarity: {best_sim:.4f}. Movies found: {len(movie_list)}")
    
    return {
        "status": "success",
        "actor": actor_name, 
        "movies": movie_list,
        "similarity": float(best_sim), 
        "message": f"Diễn viên được nhận diện: {actor_name} (Độ tương đồng: {best_sim:.2f})"
    }


# =========================
# 4. Hàm Truy vấn Nội dung (Đã cập nhật tính Sim)
# =========================

def query_by_image_resnet50_content(img_path, top_k=5, threshold=0.25):
    """
    Truy vấn nội dung (frame) phim bằng đặc trưng ResNet50.
    Trả về: {"movies": list_phim, "message": ...}
    """
    
    if FEATURE_EXTRACTOR_MODEL is None or CONTENT_INDEX is None:
        return {"movies": [], "message": "ResNet50 Content Index hoặc Model chưa tải."}

    feat = extract_resnet_feature(img_path)
    if feat is None:
        return {"movies": [], "message": "Không thể trích xuất đặc trưng ResNet50."}

    feat = feat.reshape(1, -1)
    faiss.normalize_L2(feat)
    
    D, I = CONTENT_INDEX.search(feat, top_k * 5) # D là Cosine Distance
    
    results = {} 
    
    # Lưu ý: threshold là khoảng cách tối đa cho phép.
    for dist, label_idx in zip(D[0], I[0]):
        if dist > threshold: # Lọc theo khoảng cách tối đa
            continue
            
        raw_label = str(CONTENT_LABELS[label_idx])
        cleaned_label = raw_label.split("_")[0]

        if cleaned_label not in results:
            info = get_movie_info(cleaned_label)
            if info:
                # Tính độ tương đồng (Sim = 1 - Dist)
                info["similarity"] = float(1.0 - dist) 
                results[cleaned_label] = info
                
            if len(results) >= top_k:
                break


    if not results:
        # Tính độ tương đồng tối đa cho thông báo lỗi
        max_sim = 1.0 - D[0][0] if len(D[0]) > 0 and D[0][0] != -1 else 0.0
        print(f"ResNet50 Content search found 0 results. Max similarity: {max_sim:.4f}.")
        return {"movies": [], "message": f"Không tìm thấy nội dung phim nào (Độ tương đồng tối đa: {max_sim:.2f})"}

    return {
        "movies": list(results.values()), # list các dict phim
        "message": f"Tìm thấy {len(results)} phim liên quan."
    }