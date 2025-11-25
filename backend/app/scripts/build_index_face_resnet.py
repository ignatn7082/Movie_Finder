import os
import numpy as np
import faiss
import json
import keras
from keras.models import load_model, Model
from keras.applications.resnet50 import preprocess_input
from keras.preprocessing import image
from PIL import Image, ImageEnhance

# =========================
# CONFIGURATION
# =========================

FACE_DATASET_DIR = r"F:\LV\actors_image" 
MODEL_PATH = "data/resnet50_feature_extractor_3.h5" 

# OUTPUT files
FACE_INDEX_PATH = "data/actor_resnet50_face_3.index"
FACE_LABELS_PATH = "data/actor_resnet50_face_labels_3.npy"
PROGRESS_FILE = "data/resnet_face_index_progress_3.json"

# =========================
# Helper Functions
# =========================

def normalize(vecs):
    """Chuẩn hóa L2 (unit norm) cho vector."""
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    return vecs / (norms + 1e-8)

def _process_image_to_array(img: Image.Image, target_size=(224, 224)):
    """Tiền xử lý PIL Image thành mảng NumPy sẵn sàng cho ResNet50."""
    img = img.resize(target_size)
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    return x

def augment_image(pil_img: Image.Image):
    """
    Tạo các phiên bản tăng cường dữ liệu của ảnh gốc.
    Trả về một danh sách các PIL Image đã được tăng cường.
    """
    augmented_images = [pil_img] # Ảnh gốc luôn được giữ lại
    
    # 1. Lật ngang (Horizontal Flip)
    augmented_images.append(pil_img.transpose(Image.FLIP_LEFT_RIGHT))
    
    # 2. Thay đổi độ sáng/tương phản nhẹ (Brightness/Contrast Jitter)
    # Tăng độ sáng nhẹ (Factor 1.1)
    enhancer = ImageEnhance.Brightness(pil_img)
    augmented_images.append(enhancer.enhance(1.1))
    
    # Giảm độ sáng nhẹ (Factor 0.9)
    enhancer = ImageEnhance.Brightness(pil_img)
    augmented_images.append(enhancer.enhance(0.9))
    
    # Tăng tương phản nhẹ (Factor 1.1)
    enhancer = ImageEnhance.Contrast(pil_img)
    augmented_images.append(enhancer.enhance(1.1))

    # Giảm tương phản nhẹ (Factor 0.9)
    enhancer = ImageEnhance.Contrast(pil_img)
    augmented_images.append(enhancer.enhance(0.9))
    
    return augmented_images # Trả về 6 phiên bản

def extract_face_feature_from_pil(pil_img: Image.Image, model: Model, target_size=(224, 224)):
    """
    Trích xuất đặc trưng 2048D từ ảnh khuôn mặt (PIL Image) đã được tiền xử lý.
    """
    try:
        x = _process_image_to_array(pil_img, target_size)
        
        # 1. Dự đoán (feat có shape (1, 7, 7, 2048))
        # [0] để loại bỏ chiều batch: (7, 7, 2048)
        feat = model.predict(x, verbose=0)[0] 
        
        # 2. ÁP DỤNG GLOBAL AVERAGE POOLING để giảm chiều (Fix)
        # Chuyển tensor (7, 7, 2048) thành vector (2048,)
        feat_2048d = np.mean(feat, axis=(0, 1))
        
        return feat_2048d.flatten() # Trả về vector 2048D
        
    except Exception as e:
        print(f"[WARN] Lỗi khi trích xuất feature từ PIL Image: {e}")
        return None

def save_progress(processed_files, features, labels):
    """Lưu trạng thái tiến trình hiện tại vào file JSON và NumPy."""
    # ... (Hàm này giữ nguyên) ...
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(processed_files, f)
    
    # Lưu tạm thời các đặc trưng đã trích xuất
    if features:
        np.save(FACE_LABELS_PATH + ".tmp", np.array(labels))
        np.save(FACE_INDEX_PATH + ".tmp", np.array(features))
    
    print(f"\n[INFO] Đã lưu tiến trình. {len(processed_files)} file đã xử lý.")


def load_progress():
    """Tải trạng thái tiến trình và các đặc trưng tạm thời đã lưu."""
    # ... (Hàm này giữ nguyên) ...
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
        base_model = load_model(MODEL_PATH, compile=False)
        # Lấy lớp Feature Map (Giả định lớp cuối cùng là Output Layer/Classification Layer)
        model = Model(inputs=base_model.input, outputs=base_model.layers[-2].output)
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
            
            try:
                # 2a. Tải ảnh gốc (PIL Image)
                original_img = Image.open(full_path).convert("RGB")
            except Exception as e:
                print(f"[WARN] Lỗi tải ảnh {full_path}: {e}")
                processed_files[full_path] = "FAILED_LOAD"
                continue

            # 2b. TĂNG CƯỜNG DỮ LIỆU
            augmented_images = augment_image(original_img)
            
            # 2c. Trích xuất đặc trưng cho TẤT CẢ các phiên bản
            success = 0
            for aug_img in augmented_images:
                feat = extract_face_feature_from_pil(aug_img, model) # <--- Dùng hàm mới
                
                if feat is not None:
                    X_features.append(feat)
                    y_labels.append(actor_name)
                    success += 1
            
            if success > 0:
                # Đánh dấu ảnh gốc đã được xử lý (gồm cả các phiên bản tăng cường)
                processed_files[full_path] = f"PROCESSED_{success}" 
            else:
                processed_files[full_path] = "FAILED_FEATURE_EXTRACTION"
            
            # Lưu tiến trình định kỳ (sau mỗi 500 ảnh gốc đã xử lý)
            if (len(processed_files) - len(processed_files.get("SKIPPED", [])) - len(processed_files.get("FAILED_LOAD", []))) % 500 == 0:
                 if len(X_features) > initial_count:
                    save_progress(processed_files, X_features, y_labels)
                    initial_count = len(X_features) 
                
    # Lưu lần cuối sau khi hoàn tất
    save_progress(processed_files, X_features, y_labels)

    # 3. Xây dựng Index FAISS cuối cùng
    # ... (Phần này giữ nguyên) ...
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