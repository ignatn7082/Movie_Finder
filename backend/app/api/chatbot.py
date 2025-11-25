from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
import httpx
import os
import re
import logging
import traceback
import unicodedata
from sqlalchemy.orm import Session
from sqlalchemy import or_

# --- IMPORTS DỊCH VỤ VÀ DB ---
from app.services.chatbot_service import query_by_text_chatbot, suggest_popular_movies
from app.db import SessionLocal, get_db
from app.models.movie import Movie
from app.models.role import Role 
from app.services.base_service import STATIC_URL_PREFIX

# Giả định DATA_DIR cũng được định nghĩa ở đâu đó (ví dụ: config/base_service)
DATA_DIR = os.getenv("DATA_DIR", "/app/data") 


router = APIRouter(prefix="/chat", tags=["chatbot"])
logger = logging.getLogger("chatbot")
logging.basicConfig(level=logging.INFO)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

if not GEMINI_API_KEY:
    logger.error("Missing GEMINI_API_KEY in environment")
    raise RuntimeError("Missing GEMINI_API_KEY in environment")

# --- Hàm Tiện Ích Lấy Session Cục Bộ ---
def get_db_session_local():
    """Tạo session cục bộ cho các hàm helper không phải route."""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

# ---------- Intent detection (Đã thêm cast_role) ----------

def detect_intent(prompt: str) -> str:
    """Nhận diện ý định cơ bản từ prompt, có hỗ trợ không dấu."""
    p_norm = normalize_text(prompt)
    if any(k in p_norm for k in ["tom tat", "noi dung", "gioi thieu phim", "review", "danh gia"]):
        return "summary"
    
    # NEW INTENT: cast_role - Nhận diện "diễn viên/nhân vật/vai diễn trong phim X"
    if re.search(r"(dien vien|nhan vat|vai dien)\s+trong\s+phim\s+([a-zA-Z0-9\s:À-Ỹà-ỹ]+)", p_norm):
        return "cast_role"
        
    if any(k in p_norm for k in ["dien vien", "phim cua", "phim co", "ai dong vai"]):
        return "actor"
    if any(k in p_norm for k in ["dao dien", "lam phim", "bo phim cua"]):
        return "director"
        
    if re.search(r"(goi y|de xuat|muon xem)\s+phim\s+([a-zA-Z0-9\s:À-Ỹà-ỹ]+)", p_norm):
        return "recommend_genre" 
        
    if any(k in p_norm for k in ["goi y", "de xuat", "nen xem gi", "phim hay"]):
        return "recommend_general"
        
    return "general"

def normalize_text(text: str) -> str:
    """Chuẩn hóa tiếng Việt không dấu, chữ thường, bỏ ký tự đặc biệt."""
    if not text:
        return ""
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join([c for c in text if unicodedata.category(c) != "Mn"])
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# --- Helper: extract_movie_name (Giữ nguyên) ---
def extract_movie_name(prompt: str) -> str | None:
    """Cố gắng trích tên phim từ câu hỏi bằng cách so khớp với DB."""
    norm_prompt = normalize_text(prompt)
    db = get_db_session_local()

    try:
        # 1. Tìm cụm "phim <tên>"
        match = re.search(r"phim\s+([a-zA-Z0-9\s:]+)", norm_prompt)
        candidate = match.group(1).strip() if match else None

        if candidate:
            movie = db.query(Movie).filter(
                or_(
                    Movie.title.ilike(f"%{candidate}%"),
                    Movie.original_title.ilike(f"%{candidate}%")
                )
            ).first()
            if movie:
                return movie.original_title or movie.title

        # 2. Fallback: tìm phim có tên xuất hiện trong toàn câu hỏi
        movie_titles = db.query(Movie.title, Movie.original_title).all()
        for title, orig_title in movie_titles:
            title_norm = normalize_text(str(title))
            orig_norm = normalize_text(str(orig_title))

            if title_norm and title_norm in norm_prompt:
                return orig_title or title
            if orig_norm and orig_norm in norm_prompt:
                return orig_title or title

    except Exception:
        logger.exception("extract_movie_name failed")
    finally:
        pass

    return None

# ... (find_actor_or_director_in_db, clean_reply_text, lookup_by_actor, lookup_by_director, lookup_by_genre giữ nguyên)
def find_actor_or_director_in_db(query: str, is_actor: bool = True) -> str | None:
    """Tìm tên gốc (có dấu) của Diễn viên/Đạo diễn trong DB bằng so khớp không dấu."""
    db = get_db_session_local()
    query_norm = normalize_text(query)

    try:
        if is_actor:
            names_raw = db.query(Role.actor_name).distinct().all()
        else:
            names_raw = db.query(Movie.director).distinct().all()
            
        for row in names_raw:
            name_clean = str(row[0]).strip()
            if not name_clean:
                continue
            
            if query_norm in normalize_text(name_clean):
                return name_clean
                
    except Exception:
        logger.exception("find_actor_or_director_in_db failed")
    finally:
        pass
        
    return None

_md_strip_re = re.compile(r"\*\*(.*?)\*\*")
def clean_reply_text(text: str, rag_results: list):
    text = _md_strip_re.sub(r"\1", text)
    try:
        for m in rag_results:
            title = m.get("title") or ""
            orig = m.get("original_title") or ""
            if title and orig and title in text:
                text = text.replace(title, orig)
    except Exception:
        logger.debug("Error replacing title->original", exc_info=True)
    return text

def lookup_by_actor(name: str, top_k: int = 10):
    """Tìm phim chứa tên diễn viên (sử dụng bảng Role)."""
    db = get_db_session_local()
    try:
        if isinstance(name, (list, tuple)):
            name = " ".join(map(str, name))
        query_norm = str(name).lower().strip()
        if not query_norm:
            return []
            
        roles = db.query(Role).join(Movie).filter(
            Role.actor_name.ilike(f"%{query_norm}%")
        ).limit(top_k).all()
        
        results = []
        seen_movie_ids = set()
        
        for r in roles:
            movie = r.movie
            if movie.id in seen_movie_ids:
                continue
            seen_movie_ids.add(movie.id)
            
            poster = f"{STATIC_URL_PREFIX}{movie.poster_file}" if movie.poster_file else None
            
            results.append({
                "title": movie.title,
                "original_title": movie.original_title,
                "overview": movie.overview,
                "release_date": movie.release_date,
                "director": movie.director,
                "stars": movie.stars,
                "genres_vn": movie.genres_vn,
                "poster": poster,
                "similarity": 1.0,
            })
            
        return results
    except Exception:
        logger.exception("lookup_by_actor failed")
        return []
    finally:
        pass

def lookup_by_director(name: str, top_k: int = 10):
    """Tìm phim theo tên đạo diễn (sử dụng bảng Movie)."""
    db = get_db_session_local()
    try:
        results = []
        query_norm = normalize_text(name)
        if not query_norm:
            return []

        movies = db.query(Movie).filter(
            Movie.director.ilike(f"%{query_norm}%")
        ).limit(top_k).all()

        for movie in movies:
            director = str(movie.director).strip()
            if query_norm in normalize_text(director):
                poster = f"{STATIC_URL_PREFIX}{movie.poster_file}" if movie.poster_file else None
                results.append({
                    "title": movie.title,
                    "original_title": movie.original_title,
                    "overview": movie.overview,
                    "release_date": movie.release_date,
                    "director": director,
                    "stars": movie.stars,
                    "genres_vn": movie.genres_vn,
                    "poster": poster,
                    "similarity": 1.0,
                })
        
        return results
    except Exception:
        logger.exception("lookup_by_director failed")
        return []
    finally:
        pass

def lookup_by_genre(genre_name: str, top_k: int = 10):
    """Tìm phim theo thể loại (sử dụng bảng Movie)."""
    db = get_db_session_local()
    try:
        results = []
        query_norm = normalize_text(genre_name)
        if not query_norm:
            return []

        movies = db.query(Movie).filter(
            Movie.genres_vn.ilike(f"%{query_norm}%")
        ).limit(top_k).all()

        for movie in movies:
            poster = f"{STATIC_URL_PREFIX}{movie.poster_file}" if movie.poster_file else None
            results.append({
                "title": movie.title,
                "original_title": movie.original_title,
                "overview": movie.overview,
                "release_date": movie.release_date,
                "director": movie.director,
                "stars": movie.stars,
                "genres_vn": movie.genres_vn,
                "poster": poster,
                "similarity": 1.0,
            })
        
        return results
    except Exception:
        logger.exception("lookup_by_genre failed")
        return []
    finally:
        pass

# --- NEW: Hàm tìm vai diễn theo tên phim ---
def lookup_roles_by_movie_name(db: Session, movie_name: str):
    """Tìm danh sách diễn viên và vai diễn trong phim dựa trên tên phim."""
    
    # 1. Tìm Movie
    movie = db.query(Movie).filter(
        or_(
            Movie.original_title.ilike(movie_name),
            Movie.title.ilike(movie_name)
        )
    ).first()

    if not movie:
        return None, None
        
    # 2. Tìm tất cả Roles cho Movie ID đó
    roles = db.query(Role).filter(
        Role.movie_id == movie.id
    ).all()
    
    # 3. Trích xuất thông tin
    role_list = []
    for r in roles:
        role_list.append({
            "actor_name": r.actor_name,
            "role_name": r.role_name
        })
        
    return movie, role_list


# ---------- Main POST route: multi-turn + hybrid logic ----------
@router.post("")
async def chat_with_gemini(request: Request, db: Session = Depends(get_db)): # Dependency Injection
    try:
        payload_body = await request.json()
        messages = payload_body.get("messages", []) or []
        prompt = (payload_body.get("prompt") or "").strip()
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is empty.")

        replacements = {}
        def remove_diacritics(s: str) -> str:
            if not s: return ""
            return "".join([c for c in unicodedata.normalize("NFD", str(s)) if unicodedata.category(c) != "Mn"])

        messages.append({"role": "user", "content": prompt})
        intent = detect_intent(prompt)

        # ---- Handle recommend intents ----
        if intent.startswith("recommend"):
            suggestions = []
            is_genre_search = False
            reply_prefix = "🎬 Mình gợi ý vài phim"
            
            if intent == "recommend_genre":
                raw_query = prompt.strip()
                m = re.search(r"(?:gợi\s+ý|đề\s+xuất|muốn\s+xem)\s+phim\s+([a-zA-Z0-9\s:À-Ỹà-ỹ]+)$", raw_query, flags=re.IGNORECASE)
                genre_candidate = m.group(1).strip() if m else None

                if genre_candidate:
                    is_genre_search = True
                    suggestions = lookup_by_genre(genre_candidate, top_k=5)
                    reply_prefix = f"🎬 Mình gợi ý vài phim {genre_candidate}"

            if not is_genre_search or not suggestions:
                try:
                    suggestions = suggest_popular_movies(n=5)
                    is_genre_search = False
                except Exception:
                    logger.exception("suggest_popular_movies failed")
                    suggestions = []

            if not suggestions:
                if is_genre_search:
                     reply = f"Tiếc quá, mình chưa tìm thấy phim thuộc thể loại {genre_candidate}. Bạn thử thể loại khác không?"
                else:
                     reply = "Hiện mình chưa có phim nổi bật để gợi ý. Bạn muốn thử tìm theo thể loại nào không?"
            else:
                titles = ", ".join([m.get("original_title") or m.get("title") for m in suggestions])
                reply = f"{reply_prefix}: {titles}. Bạn muốn mình tóm tắt phim nào không?"
                
            messages.append({"role": "assistant", "content": reply})
            return JSONResponse({"reply": reply, "intent": intent, "messages": messages, "related_movies": suggestions})

        # ---- NEW: Handle cast_role intent ----
        if intent == "cast_role":
            movie_name = extract_movie_name(prompt) 
            
            if movie_name:
                logger.info(f" Detected movie name for cast/role lookup: {movie_name}")
                
                # Gọi hàm lookup mới
                movie, roles = lookup_roles_by_movie_name(db, movie_name)
                
                if roles:
                    movie_title = movie.original_title or movie.title
                    
                    role_strings = [f"• {r['role_name']} do {r['actor_name']} đóng" for r in roles]
                    role_text = "\n".join(role_strings)
                    
                    reply = (
                        f"Các diễn viên và vai diễn trong phim {movie_title} là:\n"
                        f"{role_text}\n"
                        f"Bạn có muốn biết thêm chi tiết về phim này không?"
                    )
                    
                    # Prepare related_movies (chỉ 1 phim)
                    poster = f"{STATIC_URL_PREFIX}{movie.poster_file}" if movie.poster_file else None
                    related_movie = {
                        "title": movie.title,
                        "original_title": movie.original_title,
                        "overview": movie.overview,
                        "release_date": movie.release_date,
                        "director": movie.director,
                        "stars": movie.stars,
                        "genres_vn": movie.genres_vn,
                        "poster": poster
                    }
                    
                    messages.append({"role": "assistant", "content": reply})
                    return JSONResponse({
                        "reply": reply,
                        "intent": intent,
                        "messages": messages,
                        "related_movies": [related_movie]
                    })

                else:
                    reply = f"Mình chưa có thông tin chi tiết về diễn viên/vai diễn của phim {movie_name}."
                    messages.append({"role": "assistant", "content": reply})
                    return JSONResponse({
                        "reply": reply,
                        "intent": intent,
                        "messages": messages,
                        "related_movies": []
                    })
            
            reply = "Bạn muốn mình tìm diễn viên/vai diễn của phim nào? Vui lòng cho mình biết tên phim nhé."
            messages.append({"role": "assistant", "content": reply})
            return JSONResponse({"reply": reply, "intent": intent, "messages": messages, "related_movies": []})


        # ---- Handle actor / director intents via direct lookup first (Giữ nguyên logic cũ) ----
        if intent == "actor":
            raw_query = prompt.strip()
            m = re.search(r"(?:các\s+phim\s+của|phim\s+của|phim\s+của\s+diễn viên|các\s+phim\s+của|của)\s+(.+)$", raw_query, flags=re.IGNORECASE)
            name_candidate = m.group(1).strip() if m else raw_query

            matched_name = find_actor_or_director_in_db(name_candidate, is_actor=True)
            display_name = matched_name or name_candidate

            if matched_name:
                ascii_name = remove_diacritics(matched_name)
                replacements[ascii_name] = matched_name
                replacements[ascii_name.lower()] = matched_name

            direct = lookup_by_actor(display_name, top_k=10)

            if direct:
                titles = ", ".join([
                    f"{m.get('original_title') or m.get('title')} ({m.get('release_date','N/A')})"
                    for m in direct[:5]
                ])
                reply = (
                    f"À, mình tìm thấy {display_name} tham gia các phim sau: {titles}.\n"
                    "Bạn muốn mình tóm tắt phim nào không?"
                )
                messages.append({"role": "assistant", "content": reply})
                return JSONResponse({
                    "reply": reply,
                    "intent": intent,
                    "messages": messages,
                    "related_movies": direct
                })

            reply = (
                f"Tiếc quá, mình chưa thấy phim của {display_name} trong danh sách hiện có. "
            )
            messages.append({"role": "assistant", "content": reply})
            return JSONResponse({
                "reply": reply,
                "intent": intent,
                "messages": messages,
                "related_movies": []
            })

        # director branch
        if intent == "director":
            raw_query = prompt.strip()
            display_name = raw_query
            
            matched_name = find_actor_or_director_in_db(raw_query, is_actor=False)

            if matched_name:
                display_name = matched_name
                ascii_name = remove_diacritics(matched_name)
                replacements[ascii_name] = matched_name
                replacements[ascii_name.lower()] = matched_name

            direct = lookup_by_director(display_name, top_k=10)

            if direct:
                titles = ", ".join([
                    f"{m.get('original_title') or m.get('title')} ({m.get('release_date','N/A')})"
                    for m in direct[:5]
                ])
                reply = (
                    f"🎬 {display_name} là đạo diễn của các phim như: {titles}.\n"
                    "Bạn muốn mình tóm tắt phim nào không?"
                )
                messages.append({"role": "assistant", "content": reply})
                return JSONResponse({
                    "reply": reply,
                    "intent": intent,
                    "messages": messages,
                    "related_movies": direct
                })

            reply = (
                f"Mình chưa tìm thấy phim do {display_name} đạo diễn. "
                "Bạn muốn mình tìm đạo diễn khác hay thể loại phim khác không?"
            )
            messages.append({"role": "assistant", "content": reply})
            return JSONResponse({
                "reply": reply,
                "intent": intent,
                "messages": messages,
                "related_movies": []
            })
        
        try:
            rag_results = query_by_text_chatbot(prompt, top_k=5) or []
        except Exception:
            logger.exception("query_by_text_chatbot failed")
            rag_results = []


        if intent == "summary":
            movie_name = extract_movie_name(prompt) 

            if movie_name:
                logger.info(f" Detected movie name: {movie_name}")
                
                movie = db.query(Movie).filter(
                    or_(
                        Movie.original_title.ilike(movie_name),
                        Movie.title.ilike(movie_name)
                    )
                ).first()

                if movie:
                    poster = f"{STATIC_URL_PREFIX}{movie.poster_file}" if movie.poster else None
                    reply = f"{movie.original_title or movie.title} ({movie.release_date or 'N/A'}): {movie.overview or 'Không có mô tả'}"
                    messages.append({"role": "assistant", "content": reply})
                    return JSONResponse({
                        "reply": reply,
                        "intent": intent,
                        "messages": messages,
                        "related_movies": [{
                            "title": movie.title,
                            "original_title": movie.original_title,
                            "overview": movie.overview,
                            "release_date": movie.release_date,
                            "director": movie.director,
                            "stars": movie.stars,
                            "genres_vn": movie.genres_vn,
                            "poster": poster
                        }]
                    })


        # For compare/general: if rag_results empty, fallback suggestions (Giữ nguyên)
        if not rag_results:
            suggestions = []
            try:
                suggestions = suggest_popular_movies(n=5)
            except Exception:
                suggestions = []
            if suggestions:
                titles = ", ".join([m.get("original_title") or m.get("title") for m in suggestions])
                reply = f"Mình có các phim này nè: {titles}."
                messages.append({"role": "assistant", "content": reply})
                return JSONResponse({"reply": reply, "intent": "fallback_suggest", "messages": messages, "related_movies": suggestions})
            else:
                reply = "Mình chưa tìm thấy phim phù hợp. Bạn có thể cho thêm chi tiết (tên, thể loại, hoặc diễn viên) không?"
                messages.append({"role": "assistant", "content": reply})
                return JSONResponse({"reply": reply, "intent": "none", "messages": messages, "related_movies": []})

        # ---- Xây dựng context và gọi Gemini (Giữ nguyên) ----
        context_lines = []
        for r in rag_results[:5]:
            title_display = r.get("original_title") or r.get("title")
            context_lines.append(
                f"{title_display} ({r.get('release_date','N/A')}) — {r.get('genres_vn','')} — Đạo diễn: {r.get('director','')}. Diễn viên: {r.get('stars','')}"
            )
        context_text = "\n".join(context_lines)

        history = "\n".join([f"{'Người dùng' if m['role']=='user' else 'Trợ lý'}: {m['content']}" for m in messages[-5:]])

        gemini_prompt = f"""
Bạn là trợ lý phim tiếng Việt, thân thiện, trả lời ngắn gọn, tự nhiên (không dùng **bold**). 
Dưới đây là thông tin phim liên quan và lịch sử hội thoại:
Phim liên quan:
{context_text}

Hội thoại:
{history}

Câu hỏi: {prompt}

Khi nhắc tên phim, dùng tên gốc (Original Title) nếu có.
Trả lời tóm tắt, rõ ràng.
"""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(f"{GEMINI_ENDPOINT}?key={GEMINI_API_KEY}", json={"contents":[{"parts":[{"text": gemini_prompt}]}]})
            if resp.status_code != 200:
                logger.error("[Gemini] status=%s text=%s", resp.status_code, resp.text)
                raise HTTPException(status_code=502, detail="Upstream Gemini error")
            gem_data = resp.json()
            reply_text = gem_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text","")
        except HTTPException:
            raise
        except Exception:
            logger.exception("Gemini call failed")
            reply_text = ""

        reply_text = clean_reply_text(reply_text, rag_results)

        if replacements:
            for k, v in replacements.items():
                try:
                    if not k:
                        continue
                    reply_text = re.sub(re.escape(k), v, reply_text, flags=re.IGNORECASE)
                except Exception:
                    logger.debug("replacement failed for %s -> %s", k, v, exc_info=True)

        if not reply_text:
            top = rag_results[0]
            reply_text = f"{top.get('original_title') or top.get('title')} ({top.get('release_date','N/A')}): {top.get('overview','Không có mô tả')}"

        messages.append({"role":"assistant","content":reply_text})
        return JSONResponse({"reply": reply_text, "intent": intent, "messages": messages, "related_movies": rag_results})

    except HTTPException:
        raise
    except Exception:
        logger.error("[chat_with_gemini] %s", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")