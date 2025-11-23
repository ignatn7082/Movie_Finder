# app/services/text_search_service.py

import os
import faiss
import numpy as np
import json
import traceback
import random
from sentence_transformers import SentenceTransformer
from app.services.base_service import DATA_DIR,  search_by_actor_or_role_db, STATIC_URL_PREFIX, get_movie_info
from app.db import SessionLocal
from app.models.movie import Movie
from sqlalchemy import or_, func


# Cấu hình Text Search
TEXT_INDEX_PATH = os.path.join(DATA_DIR, "text.index")
TEXT_LABELS_PATH = os.path.join(DATA_DIR, "text_labels.npy")

# Tải Mô hình SentenceTransformer và Index
try:
    print("[INFO] Loading SentenceTransformer model...")
    text_model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    
    print("[INFO] Loading FAISS text index...")
    text_index = faiss.read_index(TEXT_INDEX_PATH)
    text_labels = np.load(TEXT_LABELS_PATH, allow_pickle=True)
except Exception as e:
    print(f"[ERROR] Could not load Text Search resources: {e}")
    text_model = None
    text_index = None
    text_labels = None

def query_by_text(description: str, top_k: int = 5, threshold: float = 0.25):
    """Tìm phim dựa trên mô tả hoặc tên phim.
       1) Tra trong Postgres theo title/original_title (LIKE, case-insensitive)
       2) Nếu không có kết quả, fallback xuống FAISS semantic search
    """
    
    # Debug: Kiểm tra đầu vào và sự sẵn sàng
    print(f"[DEBUG-FAISS] Query received: '{description}'")
    print(f"[DEBUG-FAISS] Parameters: top_k={top_k}, threshold={threshold}")

    # 0. validate
    if not description or not description.strip():
        print("[DEBUG-FAISS] WARNING: Description is empty.")
        return [{"title": "Mô tả/Index trống", "poster": None, "similarity": None}]

    # 1) Try DB (Postgres) search by title / original_title first
    try:
        session = SessionLocal()
        q_text = description.strip().lower()
        db_q = session.query(Movie).filter(
            or_(
                func.lower(getattr(Movie, "title", "")) .like(f"%{q_text}%"),
                func.lower(getattr(Movie, "original_title", "")) .like(f"%{q_text}%")
            )
        ).limit(top_k).all()

        if db_q:
            print(f"[DEBUG-FAISS] DB search found {len(db_q)} rows - returning DB results")
            results = []
            for m in db_q:
                # safe getters with common field names
                title = getattr(m, "title", "") or getattr(m, "Title", "") or ""
                original = getattr(m, "original_title", "") or getattr(m, "Original Title", "") or ""
                overview = getattr(m, "overview", "") or getattr(m, "Overview", "") or ""
                release = getattr(m, "release_date", "") or getattr(m, "Release Date", "") or ""
                director = getattr(m, "director", "") or getattr(m, "Director", "") or ""
                stars = getattr(m, "stars", "") or getattr(m, "Stars", "") or ""
                genres_vn = getattr(m, "genres_vn", "") or getattr(m, "Genres", "") or ""
                poster_field = getattr(m, "poster", "") or getattr(m, "PosterFile", "") or None
                poster = f"{STATIC_URL_PREFIX}{poster_field}" if isinstance(poster_field, str) and poster_field else None

                results.append({
                    "id": getattr(m, "id", None),
                    "title": title,
                    "original_title": original,
                    "overview": overview,
                    "release_date": release,
                    "director": director,
                    "stars": stars,
                    "genres_vn": genres_vn,
                    "poster": poster,
                    "similarity": 1.0,
                })
            session.close()
            return results
    except Exception as e:
        print(f"[DEBUG-FAISS] DB search failed: {e}")
        try:
            session.close()
        except Exception:
            pass
        # continue to FAISS fallback

    # 2) Fallback: existing FAISS semantic search
    if text_model is None or text_index is None or text_labels is None:
        print("[DEBUG-FAISS] ERROR: Model or Index is NOT ready.")
        return [{"title": "Lỗi: Dữ liệu tìm kiếm ngữ nghĩa chưa sẵn sàng", "poster": None}] 

    try:
        # Nhúng mô tả thành vector
        vec = text_model.encode([description], convert_to_numpy=True, normalize_embeddings=True).astype("float32")
        
        # Debug: Vector hóa
        print(f"[DEBUG-FAISS] Vector shape: {vec.shape}")
        
        # Tìm kiếm trong FAISS Index
        D, I = text_index.search(vec, top_k)
        
        # Debug: Kết quả thô từ FAISS
        print(f"[DEBUG-FAISS] Raw Distances (D): {D[0]}")
        print(f"[DEBUG-FAISS] Raw Indices (I): {I[0]}")

        results = []
        for sim, idx in zip(D[0], I[0]):
            # Kiểm tra ngưỡng tương đồng
            if sim >= threshold:
                # Try to fetch movie metadata from Postgres by label (assume label is movie id)
                try:
                    session = SessionLocal()
                    m_id = text_labels[idx]
                    try:
                        m_obj = session.get(Movie, int(m_id))
                    except Exception:
                        m_obj = None
                    if m_obj:
                        info = {
                            "id": getattr(m_obj, "id", None),
                            "title": getattr(m_obj, "title", "") or getattr(m_obj, "Title", ""),
                            "original_title": getattr(m_obj, "original_title", "") or getattr(m_obj, "Original Title", ""),
                            "overview": getattr(m_obj, "overview", "") or getattr(m_obj, "Overview", ""),
                            "release_date": getattr(m_obj, "release_date", "") or getattr(m_obj, "Release Date", ""),
                            "director": getattr(m_obj, "director", "") or getattr(m_obj, "Director", ""),
                            "stars": getattr(m_obj, "stars", "") or getattr(m_obj, "Stars", ""),
                            "genres_vn": getattr(m_obj, "genres_vn", "") or getattr(m_obj, "Genres", "") or "",
                            "poster": (f"{STATIC_URL_PREFIX}{getattr(m_obj, 'poster')}" if getattr(m_obj, 'poster', None) else None),
                            
                        }
                    else:
                        # fallback to get_movie_info (if it still exists) or skip
                        try:
                            info = get_movie_info(text_labels[idx])
                        except Exception:
                            info = {"title": "Unknown", "poster": None}
                    info["similarity"] = float(sim)
                    results.append(info)
                finally:
                    try:
                        session.close()
                    except Exception:
                        pass
                 # Debug: Hiển thị kết quả sau khi lọc theo ngưỡng
                print(f"[DEBUG-FAISS] ACCEPTED: ID {text_labels[idx]} with Similarity {sim:.4f} >= Threshold {threshold}.")
            else:
                 # Debug: Lọc kết quả
                print(f"[DEBUG-FAISS] REJECTED: ID {text_labels[idx]} with Similarity {sim:.4f} < Threshold {threshold}.")
        
        if not results:
            print(f"[DEBUG-FAISS] RESULT: NO results found. Returning error message.")
            return [{"title": "Không tìm thấy phim phù hợp", "poster": None}]
            
        print(f"[DEBUG-FAISS] RESULT: Found {len(results)} results that met the threshold. Returning results.")
        return results

    except Exception as e:
        # ------------------ Hiển thị khi xảy ra lỗi try-except ------------------
        print("[DEBUG-FAISS] ERROR: Encountered a runtime exception during FAISS processing.")
        print("[DEBUG-FAISS] STACK TRACE:")
        print(traceback.format_exc())
        return [{"title": f"Lỗi xử lý: {str(e)}", "poster": None}]

