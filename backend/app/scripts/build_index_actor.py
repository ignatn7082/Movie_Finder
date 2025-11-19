import os
import json
import numpy as np
import torch
from PIL import Image, ImageFile, UnidentifiedImageError
import cv2
import faiss
from tqdm import tqdm
from facenet_pytorch import MTCNN
import open_clip
ImageFile.LOAD_TRUNCATED_IMAGES = True

MAX_SIZE = 1024
# =================== CONFIG ===================
ACTOR_DIR = r"F:\LV\ui\backend\data\actors_image"   # folder chứa thư mục con theo diễn viên
OUT_INDEX = "data/actor_index.index"
OUT_LABELS = "data/actor_labels.json"
OUT_META = "data/actor_meta.json"
CENTROIDS_DIR = "data/actor_centroids"
PROCESSED_FILE = "data/processed_actors.json"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# =================== LOAD MODELS ===================
# CLIP
clip_model, _, preprocess = open_clip.create_model_and_transforms(
    "ViT-B-32", pretrained="openai"
)
clip_model.to(DEVICE).eval()

# MTCNN Face Detector
mtcnn = MTCNN(keep_all=True, device=DEVICE)


# =================== UTILS ===================
def safe_load_image(path):
    """Load ảnh an toàn, tránh crash vì ảnh lớn/hỏng"""
    try:
        img = Image.open(path).convert("RGB")
    except Exception as e:
        print(f"[SKIP] {path} → lỗi load ảnh: {e}")
        return None

    # Giảm kích thước lớn -> tránh MemoryError
    w, h = img.size
    if max(w, h) > MAX_SIZE:
        scale = MAX_SIZE / max(w, h)
        img = img.resize((int(w*scale), int(h*scale)), Image.LANCZOS)

    return img


def detect_face(img_path):
    """Detect khuôn mặt có kiểm soát bộ nhớ"""
    img = safe_load_image(img_path)
    if img is None:
        return None

    try:
        boxes, probs = mtcnn.detect(img)
    except Exception as e:
        print(f"[SKIP] {img_path} → detect lỗi: {e}")
        return None

    if boxes is None or len(boxes) == 0:
        return None

    # lấy mặt có xác suất cao nhất
    biggest = int(np.argmax(probs))
    x1, y1, x2, y2 = boxes[biggest].astype(int)

    return img.crop((x1, y1, x2, y2))


def extract_feature(img_pil):
    """Trích embedding từ PIL Image đã crop mặt."""
    try:
        img_tensor = preprocess(img_pil).unsqueeze(0).to(DEVICE)
        with torch.no_grad():
            feat = clip_model.encode_image(img_tensor)
        feat = feat.cpu().numpy().flatten()
        return feat / (np.linalg.norm(feat) + 1e-8)
    except Exception as e:
        print(f"[SKIP] extract_feature failed: {e}")
        return None


def safe_name(name: str) -> str:
    s = name.replace(" ", "_")
    # remove problematic chars
    for c in ('/', '\\', ':', '*', '?', '"', '<', '>', '|'):
        s = s.replace(c, "")
    return s


# ensure directories
os.makedirs(os.path.dirname(OUT_INDEX) or ".", exist_ok=True)
os.makedirs(CENTROIDS_DIR, exist_ok=True)
os.makedirs(os.path.dirname(OUT_META) or ".", exist_ok=True)

# load processed actors if present
if os.path.exists(PROCESSED_FILE):
    try:
        with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
            processed = set(json.load(f))
    except Exception:
        processed = set()
else:
    processed = set()

# load existing meta (appendable)
if os.path.exists(OUT_META):
    try:
        with open(OUT_META, "r", encoding="utf-8") as f:
            meta_list = json.load(f)
    except Exception:
        meta_list = []
else:
    meta_list = []

actor_names = sorted(os.listdir(ACTOR_DIR)) if os.path.isdir(ACTOR_DIR) else []
print(f" Tổng diễn viên: {len(actor_names)}")

try:
    for actor in tqdm(actor_names):
        actor_path = os.path.join(ACTOR_DIR, actor)
        if not os.path.isdir(actor_path):
            continue

        if actor in processed:
            # already processed, skip
            print(f"[SKIP] {actor} (already processed)")
            continue

        image_files = [
            f for f in os.listdir(actor_path)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]

        feats = []
        skipped = 0
        processed_count = 0

        for img_name in image_files:
            img_path = os.path.join(actor_path, img_name)
            try:
                face = detect_face(img_path)
                if face is None:
                    skipped += 1
                    continue  # bỏ ảnh không có mặt

                feat = extract_feature(face)
                if feat is None:
                    skipped += 1
                    continue

                feats.append(feat)
                processed_count += 1

            except Exception as e:
                skipped += 1
                print(f"[SKIP] {img_path} → {e}")
                continue

        if not feats:
            print(f"[WARN] Không có khuôn mặt dùng được cho: {actor} (skipped={skipped})")
            # still mark as processed to avoid retrying bad folders
            processed.add(actor)
            with open(PROCESSED_FILE + ".tmp", "w", encoding="utf-8") as f:
                json.dump(list(processed), f, ensure_ascii=False, indent=2)
            os.replace(PROCESSED_FILE + ".tmp", PROCESSED_FILE)
            meta_list.append({"actor": actor, "images_processed": 0, "images_skipped": skipped})
            with open(OUT_META + ".tmp", "w", encoding="utf-8") as f:
                json.dump(meta_list, f, ensure_ascii=False, indent=2)
            os.replace(OUT_META + ".tmp", OUT_META)
            continue

        # compute centroid
        try:
            feats = np.array(feats).astype("float32")
            centroid = np.mean(feats, axis=0)
            centroid /= np.linalg.norm(centroid) + 1e-8
        except Exception as e:
            print(f"[SKIP] Failed compute centroid for {actor}: {e}")
            processed.add(actor)
            with open(PROCESSED_FILE + ".tmp", "w", encoding="utf-8") as f:
                json.dump(list(processed), f, ensure_ascii=False, indent=2)
            os.replace(PROCESSED_FILE + ".tmp", PROCESSED_FILE)
            meta_list.append({"actor": actor, "images_processed": processed_count, "images_skipped": skipped})
            with open(OUT_META + ".tmp", "w", encoding="utf-8") as f:
                json.dump(meta_list, f, ensure_ascii=False, indent=2)
            os.replace(OUT_META + ".tmp", OUT_META)
            continue

        # save centroid atomically
        safe_actor = safe_name(actor)
        tmp_np = os.path.join(CENTROIDS_DIR, safe_actor + ".npy.tmp")
        out_np = os.path.join(CENTROIDS_DIR, safe_actor + ".npy")
        try:
            np.save(tmp_np, centroid)
            os.replace(tmp_np, out_np)
        except Exception as e:
            print(f"[WARN] Failed to save centroid for {actor}: {e}")

        # update meta and processed list
        meta_list.append({"actor": actor, "images_processed": processed_count, "images_skipped": skipped})
        with open(OUT_META + ".tmp", "w", encoding="utf-8") as f:
            json.dump(meta_list, f, ensure_ascii=False, indent=2)
        os.replace(OUT_META + ".tmp", OUT_META)

        processed.add(actor)
        with open(PROCESSED_FILE + ".tmp", "w", encoding="utf-8") as f:
            json.dump(list(processed), f, ensure_ascii=False, indent=2)
        os.replace(PROCESSED_FILE + ".tmp", PROCESSED_FILE)

        print(f"[OK] Processed actor={actor} images={processed_count} skipped={skipped}")

except KeyboardInterrupt:
    print("Interrupted by user — will build index from already processed actors.")
except Exception as e:
    print(f"Unexpected failure in main loop: {e}")
    print("Will attempt to build index from already processed actors.")


# =================== BUILD INDEX FROM SAVED CENTROIDS ===================
centroid_files = sorted([f for f in os.listdir(CENTROIDS_DIR) if f.lower().endswith(".npy")])
if len(centroid_files) == 0:
    print("No centroid files found. Nothing to build.")
else:
    centroids = []
    labels = []
    for fn in centroid_files:
        path = os.path.join(CENTROIDS_DIR, fn)
        try:
            c = np.load(path)
            centroids.append(c)
            # label from filename
            label = os.path.splitext(fn)[0].replace("_", " ")
            labels.append(label)
        except Exception as e:
            print(f"[WARN] Failed to load centroid {path}: {e}")

    if len(centroids) == 0:
        print("No valid centroids loaded. Aborting final index write.")
    else:
        centroids = np.array(centroids).astype("float32")
        index = faiss.IndexFlatIP(centroids.shape[1])
        index.add(centroids)
        try:
            faiss.write_index(index, OUT_INDEX)
            with open(OUT_LABELS + ".tmp", "w", encoding="utf-8") as f:
                json.dump(labels, f, ensure_ascii=False, indent=2)
            os.replace(OUT_LABELS + ".tmp", OUT_LABELS)
            with open(OUT_META + ".tmp", "w", encoding="utf-8") as f:
                json.dump(meta_list, f, ensure_ascii=False, indent=2)
            os.replace(OUT_META + ".tmp", OUT_META)
            print("\n Build actor index hoàn tất!")
            print(" Tổng diễn viên:", len(labels))
        except Exception as e:
            print(f"[ERROR] Failed to write index/labels: {e}")
