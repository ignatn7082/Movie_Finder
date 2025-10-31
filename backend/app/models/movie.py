from fastapi import APIRouter, Depends
from app.core.roles import require_role
from app.models.user import User

router = APIRouter(prefix="/api/movies", tags=["Movies"])

@router.get("/", dependencies=[Depends(require_role(["user", "editor", "admin"]))])
def get_movies():
    return {"movies": ["Bố Già", "Mai", "Lật Mặt 7"]}

@router.post("/", dependencies=[Depends(require_role(["editor", "admin"]))])
def add_movie(movie_name: str):
    return {"msg": f"Đã thêm phim {movie_name}"}

@router.delete("/{movie_id}", dependencies=[Depends(require_role(["admin"]))])
def delete_movie(movie_id: int):
    return {"msg": f"Phim có ID {movie_id} đã bị xóa"}
