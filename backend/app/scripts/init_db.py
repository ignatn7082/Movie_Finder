import os
import pandas as pd
from sqlalchemy.orm import Session
from app.db import SessionLocal, engine, Base
from app.models.user import User
from app.models.movie import Movie
from app.core.security import get_password_hash

CSV_PATH = os.path.join("data", "Movies_vi_with_poster.csv")

def init_db():
    print("  Bắt đầu tạo bảng...")
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    #  Tạo tài khoản admin mặc định
    admin_user = db.query(User).filter_by(username="admin").first()
    if not admin_user:
        admin_user = User(
            username="admin",
            email="admin@example.com",
            password=get_password_hash("123456"),  
            role="admin",
            is_active=True,
        )
        db.add(admin_user)
        print(" Đã tạo tài khoản admin mặc định (admin / 123456)")
    else:
        print(" Admin đã tồn tại, bỏ qua bước tạo tài khoản.")

    #   Nạp dữ liệu Movies nếu bảng trống
    movie_count = db.query(Movie).count()
    if movie_count == 0 and os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH).fillna("")
        movies = [
            Movie(
                title=row["Title"],
                original_title=row.get("Original Title", ""),
                release_date=row.get("Release Date", ""),
                director=row.get("Director", ""),
                stars=row.get("Stars", ""),
                genres=row.get("Genres", ""),
                overview=row.get("Overview", ""),
                poster=row.get("PosterFile", ""),
            )
            for _, row in df.iterrows()
        ]
        db.add_all(movies)
        print(f" Đã nạp {len(movies)} phim từ {CSV_PATH}")
    else:
        print(" Dữ liệu phim đã tồn tại, bỏ qua.")

    db.commit()
    db.close()
    print(" Hoàn tất khởi tạo CSDL!")


if __name__ == "__main__":
    init_db()
