from dotenv import load_dotenv
import os

load_dotenv() 

from fastapi import FastAPI
from app.api import search, movies, upload,chatbot
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from fastapi.responses import JSONResponse


from app.services import search_service

from app.api import movies  # import router


app = FastAPI(title="Film Character Search API")

# Đăng ký router

app.include_router(chatbot.router, prefix="/api", tags=["chatbot"])
app.include_router(search.router)  # hoặc include_router(search.router, prefix="")
app.include_router(movies.router, prefix="/api", tags=["movies"])
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(movies.router)


# CORS cho phép FE truy cập
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
def root():
    return {"message": "Film Character Search Backend Running"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    import traceback
    print("====== [ERROR - Chi tiết Exception] ======")
    print(traceback.format_exc())  # In ra toàn bộ lỗi chi tiết
    print("=========================================")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )



app.mount("/static", StaticFiles(directory="data"), name="static")