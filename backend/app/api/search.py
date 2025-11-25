from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Form
from fastapi.responses import JSONResponse
import os
import uuid
import shutil
import logging

# from app.services.search_service import query_by_image, query_by_text
from app.services.main_search_service import query_by_image
from app.services.text_search_service import query_by_text

logger = logging.getLogger("app.search")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

router = APIRouter(prefix="/search", tags=["search"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# 1️ --- Tìm kiếm bằng ảnh (POST) ---
# @router.post("/image")
# async def search_character(model: str = "clip", file: UploadFile = File(...)):

#     try:
#         logger.info("Incoming search/image request filename=%s content_type=%s", getattr(file, "filename", None), getattr(file, "content_type", None))

#         file_ext = os.path.splitext(file.filename)[1] if getattr(file, "filename", None) else ".jpg"
#         temp_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex}{file_ext}")

#         with open(temp_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)

#         logger.info("Saved uploaded file to %s", temp_path)

#         # call service
#         results = query_by_image(temp_path, model=model)

#         # safety: ensure keys exist
#         actor = results.get("actor") if isinstance(results, dict) else None
#         movies = results.get("movies") if isinstance(results, dict) else None

#         logger.info("query_by_image by model=%s returned actor=%s movies_count=%s", model, actor, len(movies) if movies else 0)

#         # remove temp file (keep during debug by setting env KEEP_UPLOADS=1)
#         if os.getenv("KEEP_UPLOADS", "0") != "1":
#             try:
#                 os.remove(temp_path)
#             except Exception:
#                 logger.exception("Failed to remove temp file %s", temp_path)
#         else:
#             logger.info("Keeping uploaded file for debug: %s", temp_path)

#         # return a safe verbose payload to frontend for debugging
#         return JSONResponse(content={
#             "status": "success",
#             "actor": actor,
#             "movies": movies,
#             "raw_results": results
#         })

#     except Exception as e:
#         logger.exception("search_character failed")
#         raise HTTPException(status_code=500, detail=str(e))


@router.post("/image")
async def search_character(
    model: str = Form("two_steps_resnet"), # Đổi model mặc định thành logic 2 bước mới
    file: UploadFile = File(...)
):

    try:
        logger.info("Incoming search/image request filename=%s content_type=%s model=%s", 
                    getattr(file, "filename", None), getattr(file, "content_type", None), model)

        file_ext = os.path.splitext(file.filename)[1] if getattr(file, "filename", None) else ".jpg"
        temp_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex}{file_ext}")

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 1. Gọi hàm tìm kiếm mới (logic 2 bước)
        # Hàm query_by_image đã được cập nhật để gọi query_by_image_two_steps
        results = query_by_image(temp_path, model=model) 

        # 2. Xử lý kết quả trả về từ logic 2 bước
        # Lấy dữ liệu an toàn từ dict kết quả
        actor = results.get("actor") if isinstance(results, dict) else None
        movies = results.get("movies") if isinstance(results, dict) else None
        # THÊM: Trích xuất độ tương đồng của diễn viên (Kết quả từ Bước 2)
        actor_similarities = results.get("actor_similarities") if isinstance(results, dict) else [] 
        
        logger.info("query_by_image by model=%s returned actor=%s movies_count=%s", 
                    model, actor, len(movies) if movies else 0)

        # remove temp file (keep during debug by setting env KEEP_UPLOADS=1)
        if os.getenv("KEEP_UPLOADS", "0") != "1":
            try:
                os.remove(temp_path)
            except Exception:
                logger.exception("Failed to remove temp file %s", temp_path)
        else:
            logger.info("Keeping uploaded file for debug: %s", temp_path)

        # 3. Trả về payload cho frontend
        return JSONResponse(content={
            "status": "success",
            "actor": actor,
            "movies": movies,
            # THÊM: Trả về actor_similarities để hiển thị độ tương đồng
            "actor_similarities": actor_similarities, 
            "raw_results": results # Giữ lại raw_results cho debug
        })

    except Exception as e:
        logger.exception("search_character failed")
        raise HTTPException(status_code=500, detail=str(e))

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
