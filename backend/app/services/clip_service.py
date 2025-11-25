# app/services/clip_service.py

import os
import faiss
import json
import numpy as np
from PIL import Image
from facenet_pytorch import MTCNN
import torch
from app.core.clip_loader import clip_model, preprocess, DEVICE
from app.services.base_service import safe_load_image, DATA_DIR, get_actor_movies

# Cấu hình CLIP
ACTOR_INDEX_PATH = os.path.join(DATA_DIR, "actor_index.index")
ACTOR_LABELS_JSON = os.path.join(DATA_DIR, "actor_labels.json")

# Khởi tạo MTCNN (có thể di chuyển MTCNN lên base_service nếu cả CLIP và ArcFace dùng chung)
mtcnn = MTCNN(keep_all=True, device=DEVICE)

# Tải Index và Labels
try:
    actor_index = faiss.read_index(ACTOR_INDEX_PATH)
    with open(ACTOR_LABELS_JSON, "r", encoding="utf-8") as f:
        actor_labels = json.load(f)
    print("[CLIP] Actor Index Loaded.")
except Exception as e:
    print(f"[ERROR] Could not load CLIP actor index: {e}")
    actor_index = None
    actor_labels = []

# Add explicit check/log for CLIP model availability
if clip_model is None or preprocess is None:
    print("[ERROR] CLIP model or preprocess is not loaded. Check [clip_loader.py](http://_vscodecontentref_/13) and model files.")

def extract_clip_feature(pil_img: Image.Image):
    """Trích xuất vector CLIP 512D (chuẩn hóa L2)."""
    image = preprocess(pil_img).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        feat = clip_model.encode_image(image)
        feat = feat / feat.norm(dim=-1, keepdim=True)
    return feat.cpu().numpy().flatten().astype("float32")

def detect_face_mtcnn(img_path):
    """Phát hiện khuôn mặt bằng MTCNN (dùng cho cả CLIP/ResNet)."""
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

def query_by_image_clip(img_path, top_k=5, threshold=0.35):
    """Truy vấn diễn viên bằng đặc trưng CLIP."""
    if actor_index is None:
        return {"actor": None, "movies": [], "message": "CLIP Index chưa tải."}

    face = detect_face_mtcnn(img_path)
    if face is None:
        return {"actor": None, "movies": [], "message": "Không thấy mặt người"}

    feat = extract_clip_feature(face)
    feat = feat.reshape(1, -1)
    faiss.normalize_L2(feat)

    D, I = actor_index.search(feat, top_k)
    best_sim = D[0][0]
    best_actor = actor_labels[I[0][0]]
    best_actor = (
        best_actor.replace(".npy.tmp", "")
                  .replace(".npy", "")
                  .replace(".tmp", "")
    )

    if best_sim < threshold:
        return {"actor": None, "movies": [], "message": "Không nhận diện được"}

    movies = get_actor_movies(best_actor)

    return {
        "actor": best_actor,
        "similarity": float(best_sim),
        "movies": movies
    }