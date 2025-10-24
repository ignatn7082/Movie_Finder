import os
import numpy as np
import torch
import faiss
import pandas as pd
import json
from PIL import Image
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from app.core.clip_loader import clip_model, preprocess, DEVICE, tokenize_text
from app.core.faiss_index import index as image_index, train_labels as image_labels
from app.utils.data_utils import load_movie_metadata


# =========================
# CONFIG
# =========================
movie_df = load_movie_metadata()




BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../../data")
STATIC_URL_PREFIX = "http://localhost:8000/static/"

TEXT_INDEX_PATH = os.path.join(DATA_DIR, "text.index")
TEXT_LABELS_PATH = os.path.join(DATA_DIR, "text_labels.npy")

INDEX_PATH = os.path.join(DATA_DIR, "movie_text.index")
LABELS_PATH = os.path.join(DATA_DIR, "movie_labels.npy")
META_PATH = os.path.join(DATA_DIR, "movie_metadata.json")

index = faiss.read_index(INDEX_PATH)
labels = np.load(LABELS_PATH)
metadata = json.load(open(META_PATH, "r", encoding="utf-8"))

# =========================
# Load SentenceTransformer + FAISS text index
# =========================
print("[INFO] Loading SentenceTransformer model...")
text_model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

print("[INFO] Loading FAISS text index...")
text_index = faiss.read_index(TEXT_INDEX_PATH)
text_labels = np.load(TEXT_LABELS_PATH, allow_pickle=True)


# =========================
# Lấy thông tin phim
# =========================


def get_movie_info(title_or_label: str):
    """
    Tìm thông tin phim theo tiêu đề hoặc nhãn huấn luyện.
    Trả về: title, poster URL, overview, director, stars, genres, release_date.
    """
    try:
        key = title_or_label.split("_by_")[0].replace("_", " ").strip().lower()
        row = movie_df[movie_df["Original Title"].str.lower() == key]

        if not row.empty:
            record = row.iloc[0]

            # Chuẩn hóa đường dẫn poster
            poster_file = record.get("PosterFile", "")
            if isinstance(poster_file, float) or not poster_file:
                poster_url = None
            else:
                raw_path = poster_file.replace("\\", "/")
                abs_path = os.path.join(DATA_DIR, raw_path)
                poster_url = f"{STATIC_URL_PREFIX}{raw_path}" if os.path.exists(abs_path) else None


            # Trích xuất thông tin chi tiết
            return {
                "title": record.get("Title", ""),
                "original_title": record.get("Original Title", ""),
                "overview": record.get("Overview", ""),
                "release_date": record.get("Release Date", ""),
                "director": record.get("Director", ""),
                "stars": record.get("Stars", ""),
                "genres": record.get("Genres", ""),
                "poster": poster_url,
            }

    except Exception as e:
        print(f"[WARN] Lookup lỗi cho '{title_or_label}': {e}")

    # Nếu không tìm thấy
    return {
        "title": title_or_label,
        "original_title": None,
        "overview": None,
        "release_date": None,
        "director": None,
        "stars": None,
        "genres": None,
        "poster": None,
    }





# =========================
# Chuẩn hoá vector
# =========================
def normalize(vecs: np.ndarray):
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    return vecs / (norms + 1e-8)


# =========================
# 1️ TRUY VẤN ẢNH (CLIP)
# =========================
def extract_feature(img_path: str):
    image = preprocess(Image.open(img_path)).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        feat = clip_model.encode_image(image)
    return feat.cpu().numpy().flatten()


def query_by_image(img_path: str, top_k: int = 3, threshold: float = 0.25):
    """Tìm phim qua ảnh nhân vật (CLIP)."""
    feat = normalize(extract_feature(img_path).reshape(1, -1).astype("float32"))
    D, I = image_index.search(feat, top_k)

    results = []
    for sim, idx in zip(D[0], I[0]):
        if sim >= threshold:
            info = get_movie_info(image_labels[idx])
            info["similarity"] = float(sim)
            results.append(info)

    if not results:
        return [{"title": "Không tìm thấy phim phù hợp", "poster": None, "similarity": None}]
    return results


# =========================
# 2️ TRUY VẤN TEXT (SentenceTransformer)
# =========================

def query_by_text(description: str, top_k: int = 5, threshold: float = 0.25):
    """Tìm phim dựa trên mô tả hoặc tên phim bằng SentenceTransformer."""
    if not description or not description.strip():
        return [{"title": "Mô tả trống", "poster": None, "similarity": None}]
    
    try:
        # Encode text
        vec = text_model.encode([description], convert_to_numpy=True, normalize_embeddings=True).astype("float32")
        
        # Tìm kiếm trong FAISS
        D, I = text_index.search(vec, top_k)
        results = []
        for sim, idx in zip(D[0], I[0]):
            if sim >= threshold:
                info = get_movie_info(text_labels[idx])
                info["similarity"] = float(sim)
                results.append(info)

        if not results:
            return [{"title": "Không tìm thấy phim phù hợp", "poster": None}]
        return results

    except Exception as e:
        import traceback
        print("====== [ERROR - query_by_text()] ======")
        print(traceback.format_exc())
        print("=======================================")
        return [{"title": f"Lỗi xử lý: {str(e)}", "poster": None}]



def query_by_text_chatbot(prompt: str, top_k: int = 5):
    """
    Tìm phim theo tên, mô tả, đạo diễn hoặc diễn viên.
    Kết hợp search trực tiếp + FAISS (RAG fallback).
    """
    if not prompt or not prompt.strip():
        return []

    prompt_lower = prompt.lower()
    results = []

    #  Tìm trực tiếp trong CSV (đạo diễn hoặc diễn viên)
    direct_matches = movie_df[
        movie_df["Director"].str.lower().str.contains(prompt_lower, na=False)
        | movie_df["Stars"].str.lower().str.contains(prompt_lower, na=False)
    ]

    if not direct_matches.empty:
        for _, row in direct_matches.iterrows():
            results.append({
                "title": row.get("Title", ""),
                "original_title": row.get("Original Title", ""),
                "overview": row.get("Overview", ""),
                "release_date": row.get("Release Date", ""),
                "director": row.get("Director", ""),
                "stars": row.get("Stars", ""),
                "genres": row.get("Genres", ""),
                "poster": f"{STATIC_URL_PREFIX}{row['PosterFile']}" if isinstance(row["PosterFile"], str) else None,
                "similarity": 1.0,
            })
        return results

    #  2. Nếu không có, fallback dùng FAISS text index
    try:
        vec = text_model.encode([prompt], convert_to_numpy=True, normalize_embeddings=True)
        D, I = text_index.search(vec.astype("float32"), top_k)
        for dist, idx in zip(D[0], I[0]):
            row = movie_df.iloc[idx]
            results.append({
                "title": row.get("Title", ""),
                "original_title": row.get("Original Title", ""),
                "overview": row.get("Overview", ""),
                "release_date": row.get("Release Date", ""),
                "director": row.get("Director", ""),
                "stars": row.get("Stars", ""),
                "genres": row.get("Genres", ""),
                "poster": f"{STATIC_URL_PREFIX}{row['PosterFile']}" if isinstance(row["PosterFile"], str) else None,
                "similarity": float(dist),
            })
    except Exception as e:
        print("[ERROR][query_by_text_chatbot]", e)

    return results


def suggest_popular_movies(n=5):
    """Gợi ý ngẫu nhiên vài phim nổi bật"""
    try:
        top_movies = movie_df.sort_values(by="Vote Average", ascending=False).head(20)
        sample = top_movies.sample(min(n, len(top_movies)))

        suggestions = []
        for _, row in sample.iterrows():
            suggestions.append({
                "title": row.get("Title", ""),
                "original_title": row.get("Original Title", ""),
                "overview": row.get("Overview", "")[:120] + "...",
                "genres": row.get("Genres", ""),
                "director": row.get("Director", ""),
                "poster": f"{STATIC_URL_PREFIX}{row['PosterFile']}" if isinstance(row["PosterFile"], str) else None,
            })
        return suggestions
    except Exception as e:
        print("[WARN] suggest_popular_movies():", e)
        return []
