import os
import numpy as np
import faiss
import json
import keras
from keras.models import load_model, Model
from keras.applications.resnet50 import preprocess_input
from keras.preprocessing import image
from PIL import Image

# =========================
# CONFIGURATION
# =========================

FACE_DATASET_DIR = r"F:\LV\actors_image" 
MODEL_PATH = "data/resnet50_feature_extractor_cosine.h5" 

# OUTPUT files
FACE_INDEX_PATH = "data/actor_resnet50_face.index"
FACE_LABELS_PATH = "data/actor_resnet50_face_labels.npy"
# File lưu trữ tiến trình
PROGRESS_FILE = "data/resnet_face_index_progress.json"

# =========================
# Helper Functions
# =========================

def normalize(vecs):
    """Chuẩn hóa L2 (unit norm) cho vector."""
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    return vecs / (norms + 1e-8)

def extract_face_feature(img_path, model: Model, target_size=(224, 224)):
    """Trích xuất đặc trưng 2048D từ ảnh khuôn mặt."""
    try:
        img = image.load_img(img_path, target_size=target_size)
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        feat = model.predict(x, verbose=0)
        return feat.flatten()
    except Exception as e:
        # Ghi lại lỗi nhưng không dừng script
        print(f"[WARN] Lỗi khi trích xuất {img_path}: {e}")
        return None

def save_progress(processed_files, features, labels):
    """Lưu trạng thái tiến trình hiện tại vào file JSON và NumPy."""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(processed_files, f)
    
    # Lưu tạm thời các đặc trưng đã trích xuất
    if features:
        np.save(FACE_LABELS_PATH + ".tmp", np.array(labels))
        np.save(FACE_INDEX_PATH + ".tmp", np.array(features))
    
    print(f"\n[INFO] Đã lưu tiến trình. {len(processed_files)} file đã xử lý.")


def load_progress():
    """Tải trạng thái tiến trình và các đặc trưng tạm thời đã lưu."""
    processed_files = {}
    X_features, y_labels = [], []
    
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r') as f:
                processed_files = json.load(f)
            print(f"[INFO] Tải tiến trình: {len(processed_files)} file đã xử lý trước đó.")
        except Exception as e:
            print(f"[WARN] Lỗi khi tải progress file: {e}. Bắt đầu lại từ đầu.")
            processed_files = {}

    # Tải đặc trưng tạm thời
    if os.path.exists(FACE_INDEX_PATH + ".tmp") and os.path.exists(FACE_LABELS_PATH + ".tmp"):
        try:
            X_features = np.load(FACE_INDEX_PATH + ".tmp", allow_pickle=True).tolist()
            y_labels = np.load(FACE_LABELS_PATH + ".tmp", allow_pickle=True).tolist()
            print(f"[INFO] Tải {len(X_features)} đặc trưng tạm thời.")
        except Exception as e:
            print(f"[WARN] Lỗi khi tải feature/label tạm thời: {e}. Bỏ qua file tạm.")
            X_features, y_labels = [], []
            
    return processed_files, X_features, y_labels

# =========================
# MAIN EXECUTION
# =========================

if __name__ == "__main__":
    if not os.path.exists(MODEL_PATH):
        print(f"[ERROR] KHÔNG TÌM THẤY MODEL: {MODEL_PATH}. Vui lòng kiểm tra lại đường dẫn!")
        exit()

    print("[INFO] Loading ResNet50 feature extractor...")
    try:
        model = load_model(MODEL_PATH, compile=False)
    except Exception as e:
        print(f"[FATAL] Lỗi khi tải model. Đảm bảo TensorFlow được cài đặt: {e}")
        exit()

    # 1. Tải tiến trình và đặc trưng đã lưu
    processed_files, X_features, y_labels = load_progress()
    initial_count = len(X_features)
    
    # 2. Bắt đầu/Tiếp tục trích xuất
    print(f"[INFO] Bắt đầu trích xuất/tiếp tục từ {initial_count} mẫu...")
    
    all_actors = sorted(os.listdir(FACE_DATASET_DIR))
    
    for actor_name in all_actors:
        actor_dir = os.path.join(FACE_DATASET_DIR, actor_name)
        if not os.path.isdir(actor_dir):
            continue
            
        print(f"--- Processing Actor: {actor_name} ---")
        
        for fname in os.listdir(actor_dir):
            full_path = os.path.join(actor_dir, fname)
            
            # Kiểm tra tiến trình
            if full_path in processed_files:
                continue
                
            if not fname.lower().endswith((".jpg", ".png", ".jpeg")):
                processed_files[full_path] = "SKIPPED"
                continue
            
            feat = extract_face_feature(full_path, model)
            
            if feat is not None:
                X_features.append(feat)
                y_labels.append(actor_name)
                processed_files[full_path] = "PROCESSED"
            else:
                processed_files[full_path] = "FAILED"
            
            # Lưu tiến trình định kỳ (sau mỗi 500 file)
            if (len(X_features) - initial_count) % 500 == 0 and len(X_features) > initial_count:
                save_progress(processed_files, X_features, y_labels)
                initial_count = len(X_features) # Đặt lại điểm mốc
            
    # Lưu lần cuối sau khi hoàn tất
    save_progress(processed_files, X_features, y_labels)

    # 3. Xây dựng Index FAISS cuối cùng
    X_features = np.array(X_features)
    y_labels = np.array(y_labels)

    if X_features.size == 0:
        print("[ERROR] Không có đặc trưng nào được trích xuất để xây dựng index.")
        exit()

    print("\n" + "=" * 50)
    print(f"[INFO] Bắt đầu xây dựng FAISS Index từ {X_features.shape[0]} vector...")
    
    # Chuẩn hóa L2 cuối cùng
    X_features = normalize(X_features).astype("float32")

    # Xây dựng FAISS index (IndexFlatIP cho Cosine Similarity)
    d = X_features.shape[1]
    face_index = faiss.IndexFlatIP(d)
    face_index.add(X_features)

    # Lưu index + labels (Đè lên file .tmp)
    faiss.write_index(face_index, FACE_INDEX_PATH)
    np.save(FACE_LABELS_PATH, y_labels)
    
    # Xóa file tạm và file tiến trình
    if os.path.exists(FACE_INDEX_PATH + ".tmp"): os.remove(FACE_INDEX_PATH + ".tmp")
    if os.path.exists(FACE_LABELS_PATH + ".tmp"): os.remove(FACE_LABELS_PATH + ".tmp")
    if os.path.exists(PROGRESS_FILE): os.remove(PROGRESS_FILE)

    print("[SUCCESS] Xây dựng chỉ mục hoàn tất.")
    print(f"Index: {FACE_INDEX_PATH} ({face_index.ntotal} vectors)")
    print(f"Labels: {FACE_LABELS_PATH}")
    print("=" * 50)