# app/services/vit_service.py (Đã đổi tên)

import os
import faiss
import json
import numpy as np
from PIL import Image
from facenet_pytorch import MTCNN
import torch
from typing import List, Dict
# *** ĐIỂM SỬA: Thay thế clip_loader bằng vit_loader ***
from app.core.vit_loader import vit_model, vit_preprocess, DEVICE 
from app.services.base_service import safe_load_image, DATA_DIR, get_actor_movies, get_movie_info

# Kích thước đặc trưng mới (Ví dụ: ViT-B/16 có thể là 768D)
FEATURE_DIM = 768 # Giả định kích thước đặc trưng ViT mới

# Cấu hình ViT (Đã đổi tên Index/Labels)
# *** ĐIỂM SỬA: Đổi tên các file Index/Labels để phản ánh ViT ***
ACTOR_INDEX_PATH = os.path.join(DATA_DIR, "actor_index_vit_colab.index")
ACTOR_LABELS_JSON = os.path.join(DATA_DIR, "actor_labels_vit_colab.json")

MOVIE_INDEX_PATH = os.path.join(DATA_DIR, "vit_faiss_cpu_colab.index")
MOVIE_LABELS_PATH = os.path.join(DATA_DIR, "vit_faiss_labels_colab.npy")

# Khởi tạo MTCNN (Phát hiện khuôn mặt vẫn dùng chung)
mtcnn = MTCNN(keep_all=True, device=DEVICE)

# Tải Index và Labels
try:
    actor_index = faiss.read_index(ACTOR_INDEX_PATH)
    with open(ACTOR_LABELS_JSON, "r", encoding="utf-8") as f:
        actor_labels = json.load(f)
    print("[ViT] Actor Index Loaded.")
except Exception as e:
    # *** ĐIỂM SỬA: Cập nhật thông báo lỗi ***
    print(f"[ERROR] Could not load ViT actor index: {e}") 
    actor_index = None
    actor_labels = []

# Tải Movie/Content Index và Labels (Dùng cho Bước 1)
try:
    MOVIE_INDEX = faiss.read_index(MOVIE_INDEX_PATH)
    MOVIE_LABELS = np.load(MOVIE_LABELS_PATH, allow_pickle=True)
    print("[ViT] Movie/Content Index Loaded.")
except Exception as e:
    # *** ĐIỂM SỬA: Cập nhật thông báo lỗi ***
    print(f"[ERROR] Could not load ViT movie/content index: {e}")
    MOVIE_INDEX = None
    MOVIE_LABELS = []

# Add explicit check/log for ViT model availability
if vit_model is None or vit_preprocess is None:
    # *** ĐIỂM SỬA: Cập nhật thông báo lỗi ***
    print("[ERROR] ViT model or preprocess is not loaded. Check [vit_loader.py] and model files.")


def extract_vit_feature(pil_img: Image.Image):
    """Trích xuất vector ViT (FEATURE_DIM D, chuẩn hóa L2)."""
    # *** ĐIỂM SỬA: Dùng vit_preprocess và vit_model ***
    image = vit_preprocess(pil_img).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        # Giả định ViT output là một tensor đặc trưng. Cần đảm bảo nó được chuẩn hóa.
        # Nếu ViT trả về nhiều token (patch tokens), ta thường dùng [CLS] token (token đầu tiên)
        feat = vit_model(image) 
        
        # Thường lấy đặc trưng [CLS] token nếu mô hình là ViT cơ bản
        if isinstance(feat, list) or isinstance(feat, tuple):
             # Ví dụ: Nếu ViT trả về output, ta lấy [CLS] token (output[:, 0, :])
             # Giả định vit_model trả về đặc trưng đã được tổng hợp (pooled feature)
             feat = feat[0] 
        
        # Chuẩn hóa L2
        feat = feat / feat.norm(dim=-1, keepdim=True)
        
    return feat.cpu().numpy().flatten().astype("float32")

# Hàm detect_face_mtcnn vẫn giữ nguyên vì MTCNN không thay đổi
def detect_face_mtcnn(img_path):
    """Phát hiện khuôn mặt bằng MTCNN (dùng chung)."""
    img = safe_load_image(img_path)
    if img is None:
        return None

    try:
        boxes, probs = mtcnn.detect(img)
        if boxes is None or len(boxes) == 0:
            return None

        best_idx = np.argmax(probs)
        if probs[best_idx] < 0.90: # Ngưỡng phát hiện
            return None 

        x1, y1, x2, y2 = map(int, boxes[best_idx])
        face = img.crop((x1, y1, x2, y2))
        return face

    except Exception:
        return None

# *** ĐIỂM SỬA: Đổi tên hàm và dùng extract_vit_feature ***
def extract_face_vit_feature(img_path):
    """
    Hàm 1: Trích xuất vector đặc trưng ViT của khuôn mặt phát hiện trong ảnh.
    
    Trả về: np.ndarray (vector đặc trưng) hoặc None nếu không tìm thấy khuôn mặt.
    """
    face = detect_face_mtcnn(img_path)
    if face is None:
        return None
        
    feat = extract_vit_feature(face) # Sử dụng hàm trích xuất ViT mới
    return feat

# *** ĐIỂM SỬA: Đổi tên hàm ***
def get_all_actor_similarities_vit(input_feat: np.ndarray, top_k_actors=50) -> dict:

    
    global actor_index, actor_labels
    
    if actor_index is None or not actor_labels:
        
        print("[ERROR] ViT Actor Index/Labels not loaded for comparison.")
        return {}
    
    # Chuyển 1D array thành 2D (1, FEATURE_DIM) và chuẩn hóa L2 cho FAISS
    feat = input_feat.reshape(1, -1)
    faiss.normalize_L2(feat)
    

    k = min(top_k_actors, actor_index.ntotal)
    

    D, I = actor_index.search(feat, k) 
    
    similarities = {}
    for dist, index in zip(D[0], I[0]):
        if index != -1:
            actor_name = str(actor_labels[index])
            normalized_actor_name = actor_name.replace("_", " ")
            
            # Giả định D là Cosine Similarity (IndexFlatIP)
            sim = dist
            
            similarities[normalized_actor_name] = float(sim)
            
    return similarities


def get_actor_feature_vit(actor_name: str):
    """Lấy vector đặc trưng ViT đã lưu của một diễn viên."""
    global actor_labels, actor_index # Đảm bảo biến toàn cục
    if actor_index is None:
        return None
        
    try:
        # Tìm index của diễn viên trong actor_labels
        label_index = actor_labels.index(actor_name)
        # Vector đặc trưng ViT đã được lưu trong actor_index
        feature = actor_index.reconstruct(label_index)
        return feature
    except ValueError:
        return None
    except Exception as e:
        # *** ĐIỂM SỬA: Cập nhật thông báo lỗi ***
        print(f"[ERROR] Lỗi lấy đặc trưng diễn viên ViT {actor_name}: {e}")
        return None


# *** ĐIỂM SỬA: Đổi tên hàm và dùng get_actor_feature_vit ***
def query_actor_by_image_vit(img_path, target_actor_name: str):
    """
    So sánh ảnh đầu vào (khuôn mặt) với đặc trưng của một diễn viên cụ thể bằng ViT.
    Trả về: (độ tương đồng, đặc trưng khuôn mặt đã trích)
    """
    if actor_index is None:
        # *** ĐIỂM SỬA: Cập nhật thông báo lỗi ***
        print("[ViT] Actor Index chưa tải.")
        return None, None

    # 1. Trích xuất khuôn mặt từ ảnh đầu vào
    face = detect_face_mtcnn(img_path)
    if face is None:
        return None, None

    # 2. Trích xuất đặc trưng ViT từ khuôn mặt ảnh đầu vào
    feat_input = extract_vit_feature(face) # Sử dụng hàm trích xuất ViT mới
    feat_input_normalized = feat_input.reshape(1, -1)
    faiss.normalize_L2(feat_input_normalized)

    # 3. Lấy đặc trưng của diễn viên mục tiêu từ Index
    feat_target = get_actor_feature_vit(target_actor_name) # Dùng hàm lấy đặc trưng ViT mới
    if feat_target is None:
        return None, feat_input # Trả về None sim nhưng vẫn trả về đặc trưng

    feat_target_normalized = feat_target.reshape(1, -1)
    faiss.normalize_L2(feat_target_normalized) 

    # 4. Tính toán độ tương đồng (Cosine Similarity = Tích vô hướng của vector chuẩn hóa L2)
    similarity = np.dot(feat_input_normalized, feat_target_normalized.T)[0][0]
    
    return float(similarity), feat_input # Trả về sim và đặc trưng ảnh đầu vào

# TẠM THỜI: Thêm hàm giả định cho bước 1 nếu người dùng chọn ViT (Content)
# *** ĐIỂM SỬA: Đổi tên hàm, dùng vit_model/vit_preprocess ***
def query_by_image_vit_feature_content(img_path, top_k=5, threshold=0.25):
    """
    Hàm thực hiện Bước 1: Tìm kiếm Frame/Nội dung phim bằng ViT (Vision only).
    """
    try:
        if MOVIE_INDEX is None:
            # *** ĐIỂM SỬA: Cập nhật thông báo lỗi ***
            return {"movies": [], "message": "ViT Content Index chưa tải."}
    except NameError:
        print("[ERROR] Biến MOVIE_INDEX/MOVIE_LABELS chưa được định nghĩa. Xin hãy kiểm tra lại.")
        return {"movies": [], "message": "ViT Content Index chưa được định nghĩa."}

    # 1. Tải và tiền xử lý ảnh
    img = safe_load_image(img_path)
    if img is None:
        return {"movies": [], "message": "Không thể tải hoặc xử lý ảnh đầu vào."}
    
    # *** ĐIỂM SỬA: Dùng vit_preprocess ***
    image_tensor = vit_preprocess(img).unsqueeze(0).to(DEVICE)

    # 2. Trích xuất đặc trưng của toàn bộ ảnh (Content Feature)
    with torch.no_grad():
        # *** ĐIỂM SỬA: Dùng vit_model ***
        image_features = vit_model(image_tensor)
        
    # Chuẩn bị vector cho FAISS (Sử dụng logic tương tự như extract_vit_feature)
    feat = image_features.cpu().numpy().astype('float32')
    feat = feat.reshape(1, -1)
    faiss.normalize_L2(feat)
    
    # 3. Truy vấn FAISS (Tăng số lượng truy vấn ban đầu để lọc tốt hơn)
    D, I = MOVIE_INDEX.search(feat, top_k * 5) 
    
    # 4. Xử lý và lọc kết quả trùng lặp (Logic này giữ nguyên)
    results = {} 
    
    for sim, label_idx in zip(D[0], I[0]):
        if sim < threshold:
            continue
            
        raw_label = str(MOVIE_LABELS[label_idx])
        cleaned_label = raw_label
        
        if '.' in cleaned_label:
            cleaned_label = cleaned_label.rsplit('.', 1)[0]
        
        parts = cleaned_label.rsplit("_", 1)
        
        if len(parts) > 1 and parts[1] and not parts[1].startswith('by'):
            if parts[1].isdigit() or parts[1].startswith('Frame') or parts[1].startswith('Clip'):
                cleaned_label = parts[0]

        if cleaned_label not in results:
            info = get_movie_info(cleaned_label)
            if info:
                info["similarity"] = float(sim)
                results[cleaned_label] = info
                
            if len(results) >= top_k:
                break

    if not results:
        
        print(f"[ViT_CONTENT] Search found 0 results. Max similarity: {D[0][0]:.4f}.")
        return {"movies": [], "message": f"Không tìm thấy nội dung phim nào (Độ tương đồng tối đa: {D[0][0]:.2f})"}

    return {
        "movies": list(results.values()),
        
        "message": f"Tìm thấy {len(results)} phim liên quan bằng ViT Content Search."
    }



def get_similarities_vit(
    input_feat: np.ndarray,
    top_k_actors: int = 50
) -> List[Dict[str, float]]:
    global actor_index, actor_labels

    if actor_index is None or actor_labels is None:
        print("[ERROR] FAISS index hoặc labels chưa được load!")
        return []

    if actor_index.ntotal == 0:
        print("[ERROR] FAISS index rỗng!")
        return []

    print(f"[DEBUG] FAISS index: {actor_index.ntotal} vectors | Input shape: {input_feat.shape}")

    # Chuẩn bị vector
    feat = input_feat.reshape(1, -1).astype('float32')
    faiss.normalize_L2(feat)

    k = min(top_k_actors, actor_index.ntotal)
    D, I = actor_index.search(feat, k)

    results = []
    for i in range(k):
        idx = int(I[0][i])
        dist = float(D[0][i])

        if idx == -1:
            continue

        try:
            # XỬ LÝ AN TOÀN actor_labels (có thể là bytes hoặc str)
            label = actor_labels[idx]
            if isinstance(label, bytes):
                actor_name = label.decode('utf-8', errors='ignore').strip()
            else:
                actor_name = str(label).strip()

            actor_name = actor_name.replace("_", " ")

            # Chuyển distance → similarity
            if isinstance(actor_index, faiss.IndexFlatIP):
                similarity = dist  # Inner Product = Cosine similarity
            else:
                similarity = 1.0 / (1.0 + dist)  # L2 → similarity

            results.append({
                "actor": actor_name,
                "score": round(float(similarity), 4)
            })

        except Exception as e:
            print(f"[ERROR] Lỗi xử lý label index {idx}: {e}")
            continue

    # Sắp xếp giảm dần
    results.sort(key=lambda x: x["score"], reverse=True)
    print(f"[DEBUG] Tìm thấy {len(results)} diễn viên | Top 1: {results[0] if results else 'N/A'}")

    return results