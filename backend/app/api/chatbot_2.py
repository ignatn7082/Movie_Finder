from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
import httpx
import re
import os
import logging
from sqlalchemy.orm import Session
from app.db import get_db
from app.services.chatbot.intent_service import detect_intent
from app.services.chatbot.movie_lookup_service import (
    find_movie_by_title_fuzzy,
    lookup_cast_roles,
    lookup_by_actor,
    lookup_by_director,
    _build_movie_dict,
)
from app.services.chatbot.response_service import build_cast_role_reply, build_not_found_reply
from app.services.chatbot_service import query_by_text_chatbot, suggest_popular_movies

router = APIRouter(prefix="/chat", tags=["chatbot"])
logger = logging.getLogger("chatbot")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

if not GEMINI_API_KEY:
    logger.error("Missing GEMINI_API_KEY in environment")
    raise RuntimeError("Missing GEMINI_API_KEY in environment")

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

@router.post("")
async def chat(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    prompt = data.get("prompt", "").strip()
    messages = data.get("messages", [])
    
    if not prompt:
        raise HTTPException(400, "Prompt rỗng")

    messages.append({"role": "user", "content": prompt})
    intent = detect_intent(prompt)

    # === 1. Gợi ý phim ===
    if intent.startswith("recommend"):
        movies = suggest_popular_movies(n=6)
        titles = ", ".join(m["original_title"] for m in movies)
        reply = f"Đây là vài bộ phim hay đang hot: {titles}. Bạn muốn nghe tóm tắt phim nào?"
        return JSONResponse({"reply": reply, "intent": intent, "related_movies": movies, "messages": messages})

    # === 2. Diễn viên + vai diễn trong phim ===
    if intent == "cast_role":
        movie = find_movie_by_title_fuzzy(db, prompt)
        if movie:
            movie_obj, roles = lookup_cast_roles(db, movie.original_title)
            reply = build_cast_role_reply(movie_obj, roles)
            return JSONResponse({
                "reply": reply,
                "intent": intent,
                "related_movies": [_build_movie_dict(movie_obj)],
                "messages": messages
            })
        reply = build_not_found_reply("cast_role", prompt)
        return JSONResponse({"reply": reply, "intent": intent, "related_movies": [], "messages": messages})

    # === 3. Tìm phim theo diễn viên ===
    if intent == "actor":
        actor_name, movies = lookup_by_actor(db, prompt)
        if movies:
            titles = ", ".join(f"{m['original_title']} ({m['release_date'][:4]})" for m in movies[:5])
            reply = f"{actor_name} đã tham gia các phim: {titles}. Bạn muốn biết phim nào?"
            return JSONResponse({"reply": reply, "related_movies": movies, "intent": intent, "messages": messages})
        reply = build_not_found_reply("actor", prompt)

    # === 4. Tóm tắt phim (summary) ===
    if intent == "summary":
        movie = find_movie_by_title_fuzzy(db, prompt)
        if movie:
            reply = f"**{movie.original_title}** ({movie.release_date or 'N/A'}):\n{movie.overview or 'Chưa có nội dung tóm tắt.'}"
            return JSONResponse({
                "reply": reply,
                "related_movies": [_build_movie_dict(movie)],
                "intent": intent,
                "messages": messages
            })

    # === 5. Fallback: dùng RAG + Gemini ===
    rag_results = query_by_text_chatbot(prompt, top_k=5) or []
    if not rag_results:
        suggestions = suggest_popular_movies(5)
        titles = ", ".join(m["original_title"] for m in suggestions)
        reply = f"Mình không chắc, nhưng đây là vài phim nổi bật: {titles}. Có phim nào bạn thích không?"
        return JSONResponse({
            "reply": reply,
            "related_movies": suggestions,
            "intent": "fallback",
            "messages": messages
        })

    # Xây dựng context cho Gemini
    context_lines = []
    for r in rag_results[:5]:
        title_display = r.get("original_title") or r.get("title")
        context_lines.append(
            f"{title_display} ({r.get('release_date', 'N/A')}) — {r.get('genres_vn', '')} — "
            f"Đạo diễn: {r.get('director', '')}. Diễn viên: {r.get('stars', '')}"
        )
    context_text = "\n".join(context_lines)

    history = "\n".join([f"{'Người dùng' if m['role'] == 'user' else 'Trợ lý'}: {m['content']}" for m in messages[-5:]])

    gemini_prompt = f"""
Bạn là trợ lý phim tiếng Việt, thân thiện, trả lời ngắn gọn, tự nhiên.
Phim liên quan:
{context_text}

Hội thoại:
{history}

Câu hỏi: {prompt}

Khi nhắc tên phim, dùng tên gốc (Original Title) nếu có.
Trả lời tóm tắt, rõ ràng.
"""

    # Gọi Gemini API
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{GEMINI_ENDPOINT}?key={GEMINI_API_KEY}",
                json={"contents": [{"parts": [{"text": gemini_prompt}]}]}
            )
        if resp.status_code != 200:
            raise HTTPException(502, "Lỗi kết nối Gemini")
        
        gem_data = resp.json()
        gemini_reply = gem_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
    except Exception as e:
        logger.error(f"Lỗi gọi Gemini: {e}")
        gemini_reply = "Xin lỗi, mình đang gặp trục trặc nhỏ. Bạn thử hỏi lại nhé!"

    # Clean reply (nếu cần)
    gemini_reply = clean_reply_text(gemini_reply, rag_results)  # Giả sử bạn có hàm này từ code cũ

    messages.append({"role": "assistant", "content": gemini_reply})
    return JSONResponse({
        "reply": gemini_reply,
        "intent": intent,
        "messages": messages,
        "related_movies": rag_results
    })
