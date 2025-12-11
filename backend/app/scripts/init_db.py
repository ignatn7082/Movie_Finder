# import os
# import json
# import pandas as pd
# from sqlalchemy.orm import Session
# from app.db import SessionLocal, engine, Base
# from app.models.user import User
# from app.models.movie import Movie
# from app.models.role import Role
# from app.core.security import get_password_hash


# # ====== ĐƯỜNG DẪN DỮ LIỆU ======
# CSV_PATH = os.path.join("data", "Movies_vi_with_poster.csv")
# ROLES_PATH = os.path.join("data", "roles_updated.json")
# ROLE_ID_PATH = os.path.join("data", "roles_with_movie_id.json")


# # ====== HÀM KHỞI TẠO ======
# def init_db():
#     print(" Bắt đầu khởi tạo CSDL...")
#     Base.metadata.create_all(bind=engine)
#     db: Session = SessionLocal()

#     # ===  Tạo admin mặc định ===
#     admin_user = db.query(User).filter_by(username="admin").first()
#     if not admin_user:
#         admin_user = User(
#             username="admin",
#             email="admin@example.com",
#             password=get_password_hash("123456"),
#             role="admin",
#             is_active=True,
#         )
#         db.add(admin_user)
#         db.commit()
#         print(" Đã tạo tài khoản admin mặc định (admin / 123456)")
#     else:
#         print(" Tài khoản admin đã tồn tại — bỏ qua.")

#     # ===  Nạp dữ liệu phim từ CSV nếu trống ===
#     movie_count = db.query(Movie).count()
#     if movie_count == 0 and os.path.exists(CSV_PATH):
#         df = pd.read_csv(CSV_PATH).fillna("")
#         movies = [
#             Movie(
#                 title=row["Title"],
#                 original_title=row.get("Original Title", ""),
#                 release_date=row.get("Release Date", ""),
#                 director=row.get("Director", ""),
#                 stars=row.get("Stars", ""),
#                 genres_vn=row.get("genres_vn", ""),
#                 overview=row.get("Overview", ""),
#                 poster=row.get("PosterFile", ""),
#             )
#             for _, row in df.iterrows()
#         ]
#         db.add_all(movies)
#         db.commit()
#         print(f" Đã nạp {len(movies)} phim từ {CSV_PATH}")
#     else:
#         print(f" Đã có {movie_count} phim trong CSDL — bỏ qua nạp mới.")

#     # === 3 Nạp dữ liệu role_id.json ===
#     movie_title_to_id = {}
#     if os.path.exists(ROLE_ID_PATH):
#         with open(ROLE_ID_PATH, "r", encoding="utf-8") as f:
#             role_id_data = json.load(f)
#         for item in role_id_data:
#             title = item.get("movie_title", "").strip()
#             movie_id = item.get("movie_id")
#             if title and movie_id:
#                 movie_title_to_id[title] = movie_id
#         print(f" Đã tải {len(movie_title_to_id)} phim từ role_id.json")
#     else:
#         print(" Không tìm thấy file role_id.json — sẽ chỉ dùng dò gần đúng.")

#     # ===  Nạp dữ liệu roles_updated.json ===
#     if os.path.exists(ROLES_PATH):
#         with open(ROLES_PATH, "r", encoding="utf-8") as f:
#             roles_data = json.load(f)

#         added_roles = 0
#         skipped_movies = 0

#         for movie_title, cast in roles_data.items():
#             movie_id = movie_title_to_id.get(movie_title)

#             # Tìm phim theo ID hoặc tên gốc
#             movie = None
#             if movie_id:
#                 movie = db.query(Movie).filter(Movie.id == movie_id).first()
#             else:
#                 movie = db.query(Movie).filter(Movie.original_title.ilike(f"%{movie_title}%")).first()

#             if not movie:
#                 print(f" Không tìm thấy phim '{movie_title}' — bỏ qua.")
#                 continue
            
#             cast_added = 0
#             for actor, role_name in cast.items():
#                 #  Bỏ qua khóa "movie_id" trong JSON
#                 if actor == "movie_id":
#                     continue
                
#                 exists = (
#                     db.query(Role)
#                     .filter_by(movie_id=movie.id, actor_name=actor)
#                     .first()
#                 )
#                 if not exists:
#                     db.add(Role(movie_id=movie.id, actor_name=actor, role_name=role_name))
#                     added_roles += 1
#                     cast_added += 1

#             if cast_added > 0:
#                 print(f" {movie.title}: thêm {cast_added} vai diễn.")

#         db.commit()
#         print(f"\n Tổng cộng đã thêm {added_roles} vai diễn mới.")
#         if skipped_movies > 0:
#             print(f" {skipped_movies} phim không tìm thấy trong CSDL.")
#     else:
#         print(" Không tìm thấy file roles_updated.json — bỏ qua phần vai diễn.")

#     db.close()
#     print(" Hoàn tất khởi tạo CSDL!\n")


# # ===== MAIN =====
# if __name__ == "__main__":
#     init_db()
