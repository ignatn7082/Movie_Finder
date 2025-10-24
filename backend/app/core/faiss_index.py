import os
import numpy as np
import faiss

# Trỏ đúng về thư mục gốc backend (có thư mục data/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")

INDEX_PATH = os.path.join(DATA_DIR, "clip_faiss.index")
LABELS_PATH = os.path.join(DATA_DIR, "clip_train_labels.npy")

print(f"[INFO] Loading FAISS index from {INDEX_PATH} ...")

if not os.path.exists(INDEX_PATH):
    raise FileNotFoundError(f" Không tìm thấy file index: {INDEX_PATH}")
if not os.path.exists(LABELS_PATH):
    raise FileNotFoundError(f" Không tìm thấy file labels: {LABELS_PATH}")

index = faiss.read_index(INDEX_PATH)
train_labels = np.load(LABELS_PATH)

print(f"[INFO]  FAISS index loaded successfully ({index.ntotal} vectors).")
