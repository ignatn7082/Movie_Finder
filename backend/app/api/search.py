from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import JSONResponse
import os
import uuid
import shutil

from app.services.search_service import query_by_image, query_by_text

router = APIRouter(prefix="/search", tags=["search"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# 1️ --- Tìm kiếm bằng ảnh (POST) ---
@router.post("/image")
async def search_character(file: UploadFile = File(...)):
    """
    Upload ảnh và tìm kiếm phim bằng CLIP + FAISS.
    """
    try:
        # Lưu file tạm
        file_ext = os.path.splitext(file.filename)[1]
        temp_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex}{file_ext}")

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Gọi hàm truy vấn ảnh
        results = query_by_image(temp_path, top_k=1, threshold=0.25)

        # Xoá file sau khi xử lý
        os.remove(temp_path)

        return JSONResponse(content={"results": results})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý ảnh: {str(e)}")


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
