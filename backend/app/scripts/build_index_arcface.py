import os
import json
import numpy as np
import cv2
from tqdm import tqdm

# ĐÃ LOẠI BỎ MTCNN: from mtcnn import MTCNN
from insightface.app import FaceAnalysis
import faiss

# ==============================
# CONFIG
# ==============================
# Sử dụng r"" để đảm bảo đường dẫn không bị xử lý ký tự thoát
DATA_DIR = r"F:\LV\actors_image"

OUTPUT_INDEX = "data/actor_arcface.index"
OUTPUT_LABELS = "data/actor_arcface_labels.json"
OUTPUT_PROCESSED = "data/actor_arcface_processed.json"

# Đảm bảo thư mục 'data' tồn tại
os.makedirs(os.path.dirname(OUTPUT_INDEX), exist_ok=True)


# ==============================
# LOAD “processed” SET
# ==============================
if os.path.exists(OUTPUT_PROCESSED):
    # Đọc tệp processed với encoding UTF-8
    with open(OUTPUT_PROCESSED, "r", encoding="utf-8") as f:
        processed = set(json.load(f))
else:
    processed = set()

print(f" Loaded {len(processed)} processed actors")


# ==============================
# LOAD MODELS
# ==============================
# ĐÃ LOẠI BỎ MTCNN
# print(" Loading MTCNN face detector...")
# detector = MTCNN()

print(" Loading ArcFace model (buffalo_l)...")
# Khởi tạo FaceAnalysis với module recognition/detection được phép
# Note: buffalo_l mặc định sử dụng SCRFD để phát hiện khuôn mặt
arcface = FaceAnalysis(name="buffalo_l", allowed_modules=['detection', 'recognition'])
arcface.prepare(ctx_id=0, det_size=(640, 640)) # ctx_id=0 nếu chạy GPU, ctx_id=-1 nếu chạy CPU


# ==============================
# HÀM ĐỌC ẢNH AN TOÀN VỚI UNICODE
# ==============================
def safe_imread(file_path):
    """
    Sử dụng numpy và imdecode để đọc ảnh với đường dẫn có ký tự Unicode (Tiếng Việt)
    """
    # Đọc tệp dưới dạng dữ liệu byte
    img_data = np.fromfile(file_path, dtype=np.uint8)
    # Giải mã dữ liệu byte thành ảnh
    img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)
    return img


# ==============================
# ARCface Embedding (Sử dụng FaceAnalysis trực tiếp)
# ==============================
def get_arcface_embedding(image):
    # InsightFace yêu cầu ảnh RGB
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # arcface.get() tự động thực hiện Detection và Recognition
    faces = arcface.get(rgb)

    if len(faces) == 0:
        return None, 0 # Trả về số lượng khuôn mặt = 0
    
    # Lấy khuôn mặt có điểm số phát hiện cao nhất (mặt trung tâm, rõ nhất)
    best_face = max(faces, key=lambda x: x.det_score)
    
    emb = best_face.embedding
    # Chuẩn hóa (Normalize) vector embedding
    emb = emb / np.linalg.norm(emb)
    
    return emb, len(faces)


# ==============================
# MAIN BUILD INDEX
# ==============================
def build_index():
    embeddings = []
    labels = []

    # Sử dụng os.scandir hoặc os.listdir bình thường
    actor_folders = sorted(os.listdir(DATA_DIR))

    for actor in tqdm(actor_folders, desc="Processing actors"):
        # Lấy đường dẫn đầy đủ bằng os.path.join (có thể chứa Unicode)
        actor_path = os.path.join(DATA_DIR, actor)
        if not os.path.isdir(actor_path):
            continue

        actor_name = actor.replace("_", " ")

        # ----------------------------------------------
        #  1. Skip if already processed
        # ----------------------------------------------
        if actor_name in processed:
            # print(f" SKIP: {actor_name} (already processed)")
            continue

        print(f"\n Processing actor: {actor_name}")

        actor_vectors = []
        embedding_count = 0 # Đếm số lượng embedding thành công

        # ----------------------------------------------
        # 2. Duyệt ảnh và sử dụng safe_imread
        # ----------------------------------------------
        for img_file in os.listdir(actor_path):
            img_full_path = os.path.join(actor_path, img_file)
            
            # Chỉ xử lý các tệp ảnh phổ biến
            if not img_full_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                continue

            try:
                # SỬ DỤNG HÀM ĐỌC AN TOÀN
                image = safe_imread(img_full_path)
                
                if image is None:
                    print(f"  Cannot open/read file: {img_full_path}")
                    continue
                
                # SỬ DỤNG TRỰC TIẾP ARC-FACE (không cần MTCNN)
                emb, face_count = get_arcface_embedding(image)
                
                if emb is None:
                    # In cảnh báo nếu không tìm thấy khuôn mặt
                    print(f" ArcFace cannot extract embedding (No face found): {img_file}")
                    continue

                actor_vectors.append(emb)
                embedding_count += 1

            except Exception as e:
                # In thông báo lỗi chi tiết hơn
                print(f" Error processing {img_file} in {actor_name}: {e}")

        if embedding_count == 0:
            print(f"  No embeddings for {actor_name} (0 successful images)")
            continue

        # ----------------------------------------------
        # 3. Mean embedding
        # ----------------------------------------------
        mean_emb = np.mean(actor_vectors, axis=0)
        mean_emb = mean_emb / np.linalg.norm(mean_emb)

        embeddings.append(mean_emb)
        labels.append(actor_name)

        # ----------------------------------------------
        #  4. SAVE PROGRESS
        # ----------------------------------------------
        processed.add(actor_name)
        # Sử dụng 'w' (ghi đè) mỗi lần cập nhật
        with open(OUTPUT_PROCESSED, "w", encoding="utf-8") as f:
            json.dump(list(processed), f, ensure_ascii=False, indent=4) 

        print(f" Saved {actor_name} ({embedding_count} images processed)")

    # ----------------------------------------------
    # 5. Build & Save FAISS index
    # ----------------------------------------------
    if len(embeddings) == 0:
        print("\n  Không có embedding nào được tạo. Kết thúc.")
        return

    # Convert to numpy
    embeddings = np.array(embeddings).astype("float32")

    print("\n Building FAISS index...")
    d = embeddings.shape[1]
    index = faiss.IndexFlatIP(d)
    index.add(embeddings)

    faiss.write_index(index, OUTPUT_INDEX)
    
    with open(OUTPUT_LABELS, "w", encoding="utf-8") as f:
        json.dump(labels, f, ensure_ascii=False, indent=4)

    print("\n DONE!")
    print(f" Saved: {OUTPUT_INDEX} (Index for {len(labels)} actors)")
    print(f" Saved: {OUTPUT_LABELS}")
    print(f" Saved processed: {OUTPUT_PROCESSED}")


if __name__ == "__main__":
    build_index()