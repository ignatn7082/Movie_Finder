import os
import faiss
import numpy as np
import json
import traceback
import random
from sentence_transformers import SentenceTransformer
from app.services.base_service import DATA_DIR,  search_by_actor_or_role_db, STATIC_URL_PREFIX, get_movie_info
from app.services.text_search_service import query_by_text
from app.db import SessionLocal
from app.models.movie import Movie
from sqlalchemy import or_, func

def query_by_text_chatbot(prompt: str, top_k: int = 5):
    """Tìm kiếm kết hợp: DB/Roles -> CSV (metadata) -> FAISS (semantic)."""
    if not prompt or not prompt.strip():
        return []

    prompt_lower = prompt.lower()
    
    # 1. Tìm trong DB/Roles (ưu tiên)
    role_matches = search_by_actor_or_role_db(prompt)
    if role_matches:
        print(f"[MATCH] Found {len(role_matches)} role-based results")
        return role_matches

    # 2. Tìm trong Postgres (đạo diễn hoặc diễn viên)
    try:
        session = SessionLocal()
        db_rows = session.query(Movie).filter(
            or_(
                func.lower(getattr(Movie, "director", "")).contains(prompt_lower),
                func.lower(getattr(Movie, "stars", "")).contains(prompt_lower)
            )
        ).limit(top_k).all()

        if db_rows:
            results = []
            for m in db_rows:
                results.append({
                    "id": getattr(m, "id", None),
                    "title": getattr(m, "title", "") or getattr(m, "Title", ""),
                    "original_title": getattr(m, "original_title", "") or getattr(m, "Original Title", ""),
                    "overview": getattr(m, "overview", "") or getattr(m, "Overview", ""),
                    "release_date": getattr(m, "release_date", "") or getattr(m, "Release Date", ""),
                    "director": getattr(m, "director", "") or getattr(m, "Director", ""),
                    "stars": getattr(m, "stars", "") or getattr(m, "Stars", ""),
                    "genres_vn": getattr(m, "genres_vn", "") or getattr(m, "Genres", "") or "",
                    "poster": (f"{STATIC_URL_PREFIX}{getattr(m, 'poster')}"
                               if getattr(m, 'poster', None) else None),
                    "similarity": 1.0,
                })
            session.close()
            return results
    except Exception as e:
        print(f"[DEBUG-CHATBOT] DB search failed: {e}")
        try:
            session.close()
        except Exception:
            pass

    # 3. Fallback FAISS (semantic search)
    return query_by_text(prompt, top_k=top_k)


def suggest_popular_movies(n=5):
    """Gợi ý ngẫu nhiên vài phim nổi bật"""
    try:
        session = SessionLocal()
        # attempt to order by vote_average (best-effort); fallback to id
        try:
            rows = session.query(Movie).order_by(getattr(Movie, "vote_average").desc()).limit(100).all()
        except Exception:
            rows = session.query(Movie).limit(100).all()

        if not rows:
            session.close()
            return []

        sample_rows = random.sample(rows, min(n, len(rows)))
        suggestions = []
        for m in sample_rows:
            suggestions.append({
                "id": getattr(m, "id", None),
                "title": getattr(m, "title", "") or getattr(m, "Title", ""),
                "original_title": getattr(m, "original_title", "") or getattr(m, "Original Title", ""),
                "overview": (getattr(m, "overview", "") or getattr(m, "Overview", ""))[:120] + "...",
                "genres_vn": getattr(m, "genres_vn", "") or getattr(m, "Genres", "") or "",
                "director": getattr(m, "director", "") or getattr(m, "Director", ""),
                "poster": (f"{STATIC_URL_PREFIX}{getattr(m, 'poster')}" if getattr(m, 'poster', None) else None),
            })
        session.close()
        return suggestions
    except Exception as e:
        print("[WARN] suggest_popular_movies():", e)
        try:
            session.close()
        except Exception:
            pass
        return []


