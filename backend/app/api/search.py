from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Form, Depends
from fastapi.responses import JSONResponse
import os
import uuid
import shutil
import logging
from sqlalchemy.orm import Session
from app.db import get_db


# from app.services.search_service import query_by_image, query_by_text
from app.services.main_search_service import query_by_image
from app.services.text_search_service import query_by_text

logger = logging.getLogger("app.search")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

router = APIRouter(prefix="/search", tags=["search"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/image")
async def search_character(
    mode: str = Form("actor"),        # "actor" hoặc "content"
    file: UploadFile = File(...),
    db: Session = Depends(get_db)     # ← BẮT BUỘC ĐỂ LẤY PHIM CỦA DIỄN VIÊN
):
    temp_path = None
    try:
        logger.info("Incoming /image | mode=%s | file=%s", mode, file.filename)

        # 1. Lưu file tạm
        ext = os.path.splitext(file.filename)[1].lower() or ".jpg"
        temp_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex}{ext}")
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # 2. GỌI HÀM CHÍNH – ĐÃ TRUYỀN DB VÀO
        results = query_by_image(
            img_path=temp_path,
            mode=mode,
            db=db                      # ← QUAN TRỌNG NHẤT – KHÔNG ĐƯỢC QUÊN!
        )

        # 3. Log kết quả
        detected = results.get("detected_actor")
        films = len(results.get("actor_filmography") or [])
        logger.info("Search success | mode=%s | actor=%s | films=%d", mode, detected["name"] if detected else None, films)

        # 4. Xóa file tạm (trừ khi debug)
        if os.getenv("KEEP_UPLOADS", "0") != "1":
            try:
                os.remove(temp_path)
            except:
                pass

        # 5. Trả về dữ liệu chuẩn cho frontend
        return JSONResponse(content={
            "status": "success",
            "search_mode": mode,
            "movies": results.get("movies") or [],
            "detected_actor": results.get("detected_actor"),
            "actor_filmography": results.get("actor_filmography") or [],
            "actor_similarities": results.get("actor_similarities") or [],
            "message": results.get("message", "Tìm kiếm hoàn tất"),
            "raw_results": results
        })

    except Exception as e:
        logger.exception("search_character failed")
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        raise HTTPException(status_code=500, detail="Lỗi xử lý ảnh")

# 2 --- Tìm kiếm bằng mô tả (GET) ---
@router.get("/text")
async def search_by_text(query: str = Query(..., description="Mô tả hoặc tên phim")):
    """
    Tìm kiếm phim bằng mô tả text qua CLIP (Text Encoder)
    """
    try:
        results = query_by_text(query, top_k=1, threshold=0.25)
        return JSONResponse(content={"results": results})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý text: {str(e)}")
