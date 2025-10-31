from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
import os
import re
import logging
import traceback
import unicodedata

# Import helper từ search_service (bạn cần có các hàm/biến này trong app.services.search_service)
# - query_by_text_chatbot(prompt, top_k): trả về list phim (dict) có fields: title, original_title, overview, release_date, director, stars, genres, poster, similarity
# - suggest_popular_movies(n): trả về list phim tương tự structure bên trên
# - MOVIE_DF (pandas.DataFrame) -- optional, để tìm bằng tên director/actor trực tiếp
# - STATIC_URL_PREFIX (chuỗi) -- prefix cho poster URL
from app.services.search_service import (
    query_by_text_chatbot,
    suggest_popular_movies,
    movie_df as MOVIE_DF,
    STATIC_URL_PREFIX,
)

router = APIRouter(prefix="/chat", tags=["chatbot"])
logger = logging.getLogger("chatbot")
logging.basicConfig(level=logging.INFO)


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

if not GEMINI_API_KEY:
    logger.error("Missing GEMINI_API_KEY in environment")
    raise RuntimeError("Missing GEMINI_API_KEY in environment")

# ---------- Intent detection ----------

def detect_intent(prompt: str) -> str:
    """Nhận diện ý định cơ bản từ prompt, có hỗ trợ không dấu."""
    p_norm = normalize_text(prompt)
    if any(k in p_norm for k in ["tom tat", "noi dung", "gioi thieu phim", "review", "danh gia"]):
        return "summary"
    if any(k in p_norm for k in ["dien vien", "phim cua", "phim co", "ai dong vai"]):
        return "actor"
    if any(k in p_norm for k in ["dao dien", "lam phim", "bo phim cua"]):
        return "director"
    if any(k in p_norm for k in ["goi y", "de xuat", "nen xem gi", "phim hay"]):
        return "recommend"
    return "general"

# def detect_intent(prompt: str):
#     p = prompt.lower()
#     if any(k in p for k in ["phim hay", "gợi ý", "xem gì", "đề xuất", "recommend", "gợi ý phim"]):
#         return "recommend"
#     if any(k in p for k in ["diễn viên", "đóng trong", "ai đóng", "ai diễn"]):
#         return "actor"
#     if any(k in p for k in ["đạo diễn", "chỉ đạo", "được đạo diễn bởi", "directed by"]):
#         return "director"
#     if any(k in p for k in ["tóm tắt", "nội dung", "kể về", "summary"]):
#         return "summary"
#     if any(k in p for k in ["so sánh", "khác", "giống nhau", "compare"]):
#         return "compare"
#     return "general"

def normalize_text(text: str) -> str:
    """Chuẩn hóa tiếng Việt không dấu, chữ thường, bỏ ký tự đặc biệt."""
    if not text:
        return ""
    text = text.lower().strip()
    # chuyển ký tự có dấu thành không dấu
    text = unicodedata.normalize("NFD", text)
    text = "".join([c for c in text if unicodedata.category(c) != "Mn"])
    # loại bỏ ký tự không phải chữ/số/dấu cách
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def extract_movie_name(prompt: str, movie_df) -> str | None:
    """
    Cố gắng trích tên phim từ câu hỏi như:
    - "Tóm tắt phim Bố Già"
    - "Cho mình biết nội dung phim mai"
    - "Bo Gia movie"
    """
    norm_prompt = normalize_text(prompt)

    # tìm cụm "phim <tên>"
    match = re.search(r"phim\s+([a-zA-Z0-9\s:]+)", norm_prompt)
    if match:
        candidate = match.group(1).strip()

        # so sánh không dấu với dữ liệu phim
        for _, row in movie_df.iterrows():
            title_norm = normalize_text(str(row.get("Title", "")))
            orig_norm = normalize_text(str(row.get("Original Title", "")))
            if candidate in title_norm or candidate in orig_norm:
                return row.get("Original Title") or row.get("Title")

    # fallback: tìm phim có tên xuất hiện trong toàn câu hỏi
    for _, row in movie_df.iterrows():
        title_norm = normalize_text(str(row.get("Title", "")))
        if title_norm and title_norm in norm_prompt:
            return row.get("Original Title") or row.get("Title")

    return None


def find_actor_or_director_in_df(df, query, column="Stars"):
    """
    Tìm tên tương ứng trong cột Stars hoặc Director bằng so khớp không dấu.
    Trả về tên gốc (có dấu) nếu tìm thấy.
    """
    query_norm = normalize_text(query)
    for _, row in df.iterrows():
        names_raw = str(row.get(column, "")).split(",")
        for name in names_raw:
            name_clean = name.strip()
            if not name_clean:
                continue
            if query_norm in normalize_text(name_clean):
                return name_clean  # tên gốc có dấu
    return None



# ---------- Helper: clean markdown and swap Title -> Original Title ----------
_md_strip_re = re.compile(r"\*\*(.*?)\*\*")
def clean_reply_text(text: str, rag_results: list):
    # remove bold markdown
    text = _md_strip_re.sub(r"\1", text)
    # replace Title with original_title when possible (prefer original_title)
    try:
        for m in rag_results:
            title = m.get("title") or ""
            orig = m.get("original_title") or ""
            if title and orig and title in text:
                text = text.replace(title, orig)
    except Exception:
        logger.debug("Error replacing title->original", exc_info=True)
    return text

# ---------- Helper: direct lookup by actor/director in MOVIE_DF ----------
def lookup_by_actor(name: str, top_k: int = 10):
    """Tìm phim chứa tên diễn viên (case-insensitive substring)."""
    try:
        if MOVIE_DF is None or MOVIE_DF.empty:
            return []

        # đảm bảo name là chuỗi, xử lý trường hợp nhận list hoặc None
        if isinstance(name, (list, tuple)):
            name = " ".join(map(str, name))
        name = "" if name is None else str(name)

        # chuẩn hoá tìm kiếm: lowercase và strip
        query_norm = name.lower().strip()
        if not query_norm:
            return []

        # dùng regex=False để tránh lỗi khi query chứa ký tự regex đặc biệt
        mask = MOVIE_DF["Stars"].astype(str).str.lower().str.contains(query_norm, na=False, regex=False)
        dfm = MOVIE_DF[mask]
        results = []
        for _, r in dfm.head(top_k).iterrows():
            poster = r.get("PosterFile", "")
            poster_url = f"{STATIC_URL_PREFIX}{poster}" if poster else None
            results.append({
                "title": r.get("Title", ""),
                "original_title": r.get("Original Title", ""),
                "overview": r.get("Overview", ""),
                "release_date": r.get("Release Date", ""),
                "director": r.get("Director", ""),
                "stars": r.get("Stars", ""),
                "genres": r.get("Genres", ""),
                "poster": poster_url,
                "similarity": 1.0,
            })
        return results
    except Exception:
        logger.exception("lookup_by_actor failed")
        return []

def lookup_by_director(name: str, top_k: int = 10):
    """Tìm phim theo tên đạo diễn (tự động bỏ dấu, hỗ trợ gõ không dấu)."""
    if MOVIE_DF is None or MOVIE_DF.empty:
        return []

    results = []
    query_norm = normalize_text(name)

    for _, row in MOVIE_DF.iterrows():
        director = str(row.get("Director", "")).strip()
        director_norm = normalize_text(director)
        if query_norm and query_norm in director_norm:
            results.append({
                "title": row.get("Title", ""),
                "original_title": row.get("Original Title", ""),
                "overview": row.get("Overview", ""),
                "release_date": row.get("Release Date", ""),
                "director": director,
                "stars": row.get("Stars", ""),
                "genres": r.get("Genres", ""),
                "poster": f"{STATIC_URL_PREFIX}{row.get('PosterFile')}" if row.get("PosterFile") else None
            })

    # Xóa trùng
    seen = set()
    unique_results = []
    for r in results:
        key = r.get("original_title", r.get("title"))
        if key not in seen:
            seen.add(key)
            unique_results.append(r)

    return unique_results[:top_k]


# ---------- Main POST route: multi-turn + hybrid logic ----------
@router.post("")
async def chat_with_gemini(request: Request):
    """
    Body JSON:
    {
      "messages": [{ "role": "user"|"assistant", "content": "..." }],
      "prompt": "tin nhắn mới"
    }
    """
    try:
        payload_body = await request.json()
        messages = payload_body.get("messages", []) or []
        prompt = (payload_body.get("prompt") or "").strip()
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is empty.")

        # replacements map: ascii_without_diacritics -> original_name_with_diacritics
        replacements = {}

        # helper to remove diacritics (keeps spaces/letters)
        def remove_diacritics(s: str) -> str:
            if not s:
                return ""
            return "".join([c for c in unicodedata.normalize("NFD", str(s)) if unicodedata.category(c) != "Mn"])

        # append user message
        messages.append({"role": "user", "content": prompt})
        intent = detect_intent(prompt)

        # ---- Handle recommend intent locally ----
        if intent == "recommend":
            suggestions = []
            try:
                suggestions = suggest_popular_movies(n=5)
            except Exception:
                logger.exception("suggest_popular_movies failed")
                suggestions = []

            if not suggestions:
                reply = "Hiện mình chưa có phim nổi bật để gợi ý. Bạn muốn thử tìm theo thể loại nào không?"
            else:
                titles = ", ".join([m.get("original_title") or m.get("title") for m in suggestions])
                reply = f"🎬 Mình gợi ý vài phim nổi bật: {titles}. Bạn muốn mình tóm tắt phim nào không?"
            messages.append({"role": "assistant", "content": reply})
            return JSONResponse({"reply": reply, "intent": intent, "messages": messages, "related_movies": suggestions})

        # ---- Handle actor / director intents via direct lookup first ----
        if intent == "actor":
            raw_query = prompt.strip()
            m = re.search(r"(?:các\s+phim\s+của|phim\s+của|phim\s+của\s+diễn viên|các\s+phim\s+của|của)\s+(.+)$", raw_query, flags=re.IGNORECASE)
            name_candidate = m.group(1).strip() if m else raw_query

            matched_name = None
            if MOVIE_DF is not None:
                matched_name = find_actor_or_director_in_df(MOVIE_DF, name_candidate, column="Stars")

            display_name = matched_name or name_candidate

            # if we found canonical name with diacritics, register replacement
            if matched_name:
                ascii_name = remove_diacritics(matched_name)
                # also register lowercased ascii -> original for safety
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
                # ensure reply uses display_name (already does)
                messages.append({"role": "assistant", "content": reply})
                return JSONResponse({
                    "reply": reply,
                    "intent": intent,
                    "messages": messages,
                    "related_movies": direct
                })

            # không tìm thấy phim tương ứng
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

        # director branch: register replacements similarly if matched
        if intent == "director":
            raw_query = prompt.strip()
            display_name = raw_query
            query_norm = normalize_text(raw_query)
            matched_name = None
            if MOVIE_DF is not None:
                for _, row in MOVIE_DF.iterrows():
                    director = str(row.get("Director", "")).strip()
                    if not director:
                        continue
                    if query_norm in normalize_text(director):
                        matched_name = director
                        break
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
            movie_name = extract_movie_name(prompt, MOVIE_DF) if MOVIE_DF is not None else None

            # Nếu nhận diện được tên phim
            if movie_name:
                logger.info(f" Detected movie name: {movie_name}")
                row = MOVIE_DF[MOVIE_DF["Original Title"].astype(str).str.lower() == movie_name.lower()]
                if row.empty:
                    row = MOVIE_DF[MOVIE_DF["Title"].astype(str).str.lower() == movie_name.lower()]

                if not row.empty:
                    r = row.iloc[0]
                    poster = r.get("PosterFile", "")
                    poster_url = f"{STATIC_URL_PREFIX}{poster}" if poster else None
                    reply = f"{r.get('Original Title') or r.get('Title')} ({r.get('Release Date','N/A')}): {r.get('Overview','Không có mô tả')}"
                    messages.append({"role": "assistant", "content": reply})
                    return JSONResponse({
                        "reply": reply,
                        "intent": intent,
                        "messages": messages,
                        "related_movies": [{
                            "title": r.get("Title",""),
                            "original_title": r.get("Original Title",""),
                            "overview": r.get("Overview",""),
                            "release_date": r.get("Release Date",""),
                            "director": r.get("Director",""),
                            "stars": r.get("Stars",""),
                            "genres": r.get("Genres",""),
                            "poster": poster_url
                        }]
                    })



        # For compare/general: if rag_results empty, fallback suggestions
        if not rag_results:
            # If no RAG results and user not actor/director/summary/recommend, try suggest
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

        # ---- At this point we have rag_results and user didn't ask actor/director/summary/recommend directly
        # Build concise context for Gemini (limit length)
        context_lines = []
        for r in rag_results[:5]:
            title_display = r.get("original_title") or r.get("title")
            context_lines.append(
                f"{title_display} ({r.get('release_date','N/A')}) — {r.get('genres','')} — Đạo diễn: {r.get('director','')}. Diễn viên: {r.get('stars','')}"
            )
        context_text = "\n".join(context_lines)

        # Compose history (last 5)
        history = "\n".join([f"{'Người dùng' if m['role']=='user' else 'Trợ lý'}: {m['content']}" for m in messages[-5:]])

        # Compose Gemini prompt with instruction to avoid markdown bold and prefer original titles
        gemini_prompt = f"""
Bạn là trợ lý phim tiếng Việt, thân thiện, trả lời ngắn gọn, tự nhiên (không dùng **bold**). 
Dưới đây là thông tin phim liên quan và lịch sử hội thoại:
Phim liên quan:
{context_text}

Hội thoại:
{history}

Câu hỏi: {prompt}

Khi nhắc tên phim, dùng tên gốc (Original Title) nếu có.
Trả lời tóm tắt, rõ ràng, có thể gợi ý 2-3 phim liên quan.
"""

        # Call Gemini
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

        # Clean and replace titles with original_title if needed
        reply_text = clean_reply_text(reply_text, rag_results)

        # --- NEW: apply replacements so ascii mentions become original with diacritics ---
        if replacements:
            for k, v in replacements.items():
                try:
                    if not k:
                        continue
                    # replace case-insensitive occurrences of the ascii form with the original name
                    reply_text = re.sub(re.escape(k), v, reply_text, flags=re.IGNORECASE)
                except Exception:
                    logger.debug("replacement failed for %s -> %s", k, v, exc_info=True)

        if not reply_text:
            top = rag_results[0]
            reply_text = f"{top.get('original_title') or top.get('title')} ({top.get('release_date','N/A')}): {top.get('overview','Không có mô tả')}"

        # add assistant message and return
        messages.append({"role":"assistant","content":reply_text})
        return JSONResponse({"reply": reply_text, "intent": intent, "messages": messages, "related_movies": rag_results})

    except HTTPException:
        raise
    except Exception:
        logger.error("[chat_with_gemini] %s", traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")
