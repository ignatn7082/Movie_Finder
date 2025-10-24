# from fastapi import APIRouter, HTTPException, Request
# from fastapi.responses import JSONResponse
# import httpx
# import os
# import re
# import logging
# import traceback
# from dotenv import load_dotenv
# from app.services.search_service import query_by_text, query_by_text_chatbot

# # =====================================================
# #  Cấu hình
# # =====================================================
# load_dotenv()

# router = APIRouter(prefix="/chat", tags=["chatbot"])

# logger = logging.getLogger("chatbot")
# logging.basicConfig(level=logging.INFO)

# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# GEMINI_ENDPOINT = (
#     "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
# )

# if not GEMINI_API_KEY:
#     raise RuntimeError(" Missing GEMINI_API_KEY in .env")

# # =====================================================
# #  Bộ nhận dạng mục đích câu hỏi
# # =====================================================
# def detect_intent(prompt: str):
#     p = prompt.lower()
#     if any(k in p for k in ["diễn viên", "đóng trong", "vai", "ai đóng"]):
#         return "actor"
#     if any(k in p for k in ["đạo diễn", "chỉ đạo", "làm phim", "của ai"]):
#         return "director"
#     if any(k in p for k in ["tóm tắt", "nội dung", "kể về"]):
#         return "summary"
#     if any(k in p for k in ["gợi ý", "giống", "tương tự"]):
#         return "similar"
#     return "general"

# # =====================================================
# #  Multi-turn Chat
# # =====================================================
# @router.post("")
# async def chat_with_gemini(request: Request):
#     """
#     Nhận body dạng:
#     {
#         "messages": [{ "role": "user"|"assistant", "content": "..." }],
#         "prompt": "tin nhắn mới"
#     }
#     """
#     try:
#         data = await request.json()
#         messages = data.get("messages", [])
#         prompt = data.get("prompt", "").strip()

#         if not prompt:
#             raise HTTPException(status_code=400, detail="Prompt is empty.")

#         # Thêm tin nhắn người dùng
#         messages.append({"role": "user", "content": prompt})

#         #  Nhận dạng mục đích
#         intent = detect_intent(prompt)

#         #  RAG: lấy phim liên quan
#         rag_results = query_by_text_chatbot(prompt, top_k=5) or []
#         context = "\n".join([
#             f"- {r.get('original_title', r.get('title'))} "
#             f"({r.get('release_date','N/A')}) – {r.get('genres','')} – "
#             f"Đạo diễn: {r.get('director','?')}, Diễn viên: {r.get('stars','')}"
#             for r in rag_results if isinstance(r, dict)
#         ]) or "Không có phim liên quan trong cơ sở dữ liệu."

#         #  Ghép lịch sử hội thoại gần nhất
#         history = "\n".join([
#             f"{'Người dùng' if m['role']=='user' else 'Trợ lý'}: {m['content']}"
#             for m in messages[-5:]
#         ])
        
#         if not rag_results:
#             if intent == "actor":
#                 reply = f"Mình không thấy diễn viên {prompt} trong danh sách phim. Bạn có muốn tìm người khác không?"
#                 return JSONResponse({"reply": reply, "messages": messages, "related_movies": []})
#             elif intent == "director":
#                 reply = f"Mình không thấy đạo diễn {prompt} trong cơ sở dữ liệu. Bạn muốn mình gợi ý phim khác không?"
#                 return JSONResponse({"reply": reply, "messages": messages, "related_movies": []})



#         #  Prompt gửi lên Gemini
#         role_prompt = f"""
#         Bạn là trợ lý phim AI thân thiện, nói tiếng Việt tự nhiên.
#         Dưới đây là dữ liệu phim và hội thoại gần nhất, hãy phản hồi ngắn gọn, tự nhiên, không dùng dấu ** **.

#         🎬 Thông tin phim:
#         {context}

#         💬 Hội thoại gần đây:
#         {history}

#         Câu hỏi hiện tại: {prompt}
#         """

#         payload = {"contents": [{"parts": [{"text": role_prompt}]}]}

#         #  Gọi Gemini API
#         async with httpx.AsyncClient(timeout=40.0) as client:
#             res = await client.post(
#                 f"{GEMINI_ENDPOINT}?key={GEMINI_API_KEY}",
#                 json=payload
#             )

#         if res.status_code != 200:
#             logger.error(f"[Gemini API] {res.status_code} {res.text}")
#             raise HTTPException(status_code=502, detail=f"Gemini upstream error ({res.status_code})")

#         data = res.json()
#         reply = (
#             data.get("candidates", [{}])[0]
#             .get("content", {})
#             .get("parts", [{}])[0]
#             .get("text", "")
#         ) or "🤖 Xin lỗi, mình chưa có câu trả lời phù hợp."

       
#         reply = re.sub(r"\*\*(.*?)\*\*", r"\1", reply)

        
#         for movie in rag_results:
#             title = movie.get("title", "")
#             original = movie.get("original_title", "")
#             if title and original and title in reply:
#                 reply = reply.replace(title, original)

#         # Thêm tin nhắn phản hồi
#         messages.append({"role": "assistant", "content": reply})

#         return JSONResponse({
#             "reply": reply,
#             "intent": intent,
#             "messages": messages,
#             "related_movies": rag_results
#         })

#     except Exception as e:
#         logger.error("[chat_with_gemini] %s", traceback.format_exc())
#         raise HTTPException(status_code=500, detail="Internal server error")


from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
import os
import re
import logging
import traceback

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

# Load API key from env (ensure you call load_dotenv() in main.py)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Use a model available to your key (adjust if needed based on models_list.json)
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

if not GEMINI_API_KEY:
    logger.error("Missing GEMINI_API_KEY in environment")
    raise RuntimeError("Missing GEMINI_API_KEY in environment")

# ---------- Intent detection ----------
def detect_intent(prompt: str):
    p = prompt.lower()
    if any(k in p for k in ["phim hay", "gợi ý", "xem gì", "đề xuất", "recommend", "gợi ý phim"]):
        return "recommend"
    if any(k in p for k in ["diễn viên", "đóng trong", "ai đóng", "ai diễn"]):
        return "actor"
    if any(k in p for k in ["đạo diễn", "chỉ đạo", "được đạo diễn bởi", "directed by"]):
        return "director"
    if any(k in p for k in ["tóm tắt", "nội dung", "kể về", "summary"]):
        return "summary"
    if any(k in p for k in ["so sánh", "khác", "giống nhau", "compare"]):
        return "compare"
    return "general"

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
        if MOVIE_DF is None:
            return []
        mask = MOVIE_DF["Stars"].astype(str).str.lower().str.contains(name.lower(), na=False)
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
    except Exception as e:
        logger.exception("lookup_by_actor failed")
        return []

def lookup_by_director(name: str, top_k: int = 10):
    try:
        if MOVIE_DF is None:
            return []
        mask = MOVIE_DF["Director"].astype(str).str.lower().str.contains(name.lower(), na=False)
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
        logger.exception("lookup_by_director failed")
        return []

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
            # try direct lookup by actor name in prompt (extract name heuristically)
            # simplest: use whole prompt (user likely typed 'phim Trấn Thành' or 'Trấn Thành')
            actor_name = prompt
            direct = lookup_by_actor(actor_name, top_k=10)
            if direct:
                # respond listing found movies (use original_title)
                titles = ", ".join([m.get("original_title") or m.get("title") for m in direct[:5]])
                reply = f"Mình tìm thấy {len(direct)} phim có diễn viên {actor_name}. Ví dụ: {titles}. Bạn muốn tóm tắt phim nào?"
                messages.append({"role": "assistant", "content": reply})
                return JSONResponse({"reply": reply, "intent": intent, "messages": messages, "related_movies": direct})
            # if none, ask clarifying question
            reply = f"Mình không thấy {actor_name} trong danh sách diễn viên của dữ liệu. Bạn muốn mình tìm diễn viên khác không?"
            messages.append({"role": "assistant", "content": reply})
            return JSONResponse({"reply": reply, "intent": intent, "messages": messages, "related_movies": []})

        if intent == "director":
            director_name = prompt
            direct = lookup_by_director(director_name, top_k=10)
            if direct:
                titles = ", ".join([m.get("original_title") or m.get("title") for m in direct[:5]])
                reply = f"Mình tìm thấy {len(direct)} phim đạo diễn bởi {director_name}. Ví dụ: {titles}. Bạn muốn tóm tắt phim nào?"
                messages.append({"role": "assistant", "content": reply})
                return JSONResponse({"reply": reply, "intent": intent, "messages": messages, "related_movies": direct})
            reply = f"Mình không thấy đạo diễn {director_name} trong cơ sở dữ liệu. Bạn muốn tìm đạo diễn khác không?"
            messages.append({"role": "assistant", "content": reply})
            return JSONResponse({"reply": reply, "intent": intent, "messages": messages, "related_movies": []})

        # ---- For summary / compare / general: use RAG first ----
        rag_results = []
        try:
            rag_results = query_by_text_chatbot(prompt, top_k=5) or []
        except Exception:
            logger.exception("query_by_text_chatbot failed")
            rag_results = []

        # If user asked summary for a specific title, try to find exact match first:
        if intent == "summary":
            # try to match original_title or title in dataset
            exact_matches = []
            try:
                if MOVIE_DF is not None:
                    q = prompt.lower()
                    # try exact original title / title substring match
                    mask = MOVIE_DF["Original Title"].astype(str).str.lower() == q
                    if mask.sum() == 0:
                        mask = MOVIE_DF["Original Title"].astype(str).str.lower().str.contains(q, na=False) | \
                               MOVIE_DF["Title"].astype(str).str.lower().str.contains(q, na=False)
                    exact_matches = MOVIE_DF[mask]
            except Exception:
                logger.debug("Exact title match failed", exc_info=True)

            if not exact_matches.empty:
                row = exact_matches.iloc[0]
                poster = row.get("PosterFile", "")
                poster_url = f"{STATIC_URL_PREFIX}{poster}" if poster else None
                reply = f"{row.get('Original Title') or row.get('Title')} ({row.get('Release Date','N/A')}): {row.get('Overview','Không có mô tả')}"
                messages.append({"role": "assistant", "content": reply})
                return JSONResponse({
                    "reply": reply,
                    "intent": intent,
                    "messages": messages,
                    "related_movies": [{
                        "title": row.get("Title",""),
                        "original_title": row.get("Original Title",""),
                        "overview": row.get("Overview",""),
                        "release_date": row.get("Release Date",""),
                        "director": row.get("Director",""),
                        "stars": row.get("Stars",""),
                        "genres": row.get("Genres",""),
                        "poster": poster_url
                    }]
                })

            # else if rag_results available, use first match overview to answer shortly (avoid calling Gemini)
            if rag_results:
                top = rag_results[0]
                reply = f"{top.get('original_title') or top.get('title')} ({top.get('release_date','N/A')}): {top.get('overview','Không có mô tả')} "
                messages.append({"role": "assistant", "content": reply})
                return JSONResponse({"reply": reply, "intent": intent, "messages": messages, "related_movies": rag_results})

            # if still nothing, ask user
            reply = "Mình không có thông tin về phim đó trong danh sách. Bạn có muốn hỏi phim khác không?"
            messages.append({"role": "assistant", "content": reply})
            return JSONResponse({"reply": reply, "intent": intent, "messages": messages, "related_movies": []})

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
        if not reply_text:
            # fallback to simple summary from RAG
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
