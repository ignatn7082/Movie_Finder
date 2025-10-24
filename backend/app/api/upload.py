from fastapi import APIRouter, UploadFile

router = APIRouter()

@router.post("/upload")
async def upload_video(file: UploadFile):
    # TODO: lưu file video và trích frame
    return {"filename": file.filename, "status": "uploaded"}
