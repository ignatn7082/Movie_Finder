import os
import json
from sqlalchemy.orm import Session
from app.db import SessionLocal, Base, engine
from app.models.role import Role

DATA_DIR = os.path.join("data")
ROLE_FILE = os.path.join(DATA_DIR, "roles_updated.json")
ROLE_ID_FILE = os.path.join(DATA_DIR, "roles_with_movie_id.json")


def sync_roles():
    """Nạp dữ liệu vai diễn từ role.json và role_id.json vào CSDL"""
    db: Session = SessionLocal()
    Base.metadata.create_all(bind=engine)

    # Đọc file JSON
    if not os.path.exists(ROLE_FILE) or not os.path.exists(ROLE_ID_FILE):
        print(" Thiếu file role.json hoặc role_id.json!")
        return

    with open(ROLE_FILE, "r", encoding="utf-8") as f:
        roles_data = json.load(f)

    with open(ROLE_ID_FILE, "r", encoding="utf-8") as f:
        role_ids = json.load(f)

    # Tạo dictionary {movie_title_lower: movie_id}
    movie_id_map = {
        item["movie_title"].strip().lower(): item["movie_id"]
        for item in role_ids
    }

    # Xóa dữ liệu cũ
    print("  Xóa dữ liệu cũ trong bảng roles...")
    deleted = db.query(Role).delete()
    db.commit()
    print(f"→ Đã xóa {deleted} bản ghi cũ.\n")

    added, skipped = 0, 0

    # Duyệt từng phim trong role.json
    for movie_title, role_info in roles_data.items():
        movie_title_clean = movie_title.strip().lower()
        movie_id = role_info.get("movie_id") or movie_id_map.get(movie_title_clean)

        if not movie_id:
            print(f" Không có movie_id cho '{movie_title}' — bỏ qua.")
            skipped += 1
            continue

        for actor, character in role_info.items():
            if actor == "movie_id":
                continue

            role = Role(
                movie_id=movie_id,
                movie_title=movie_title,
                actor=actor,
                character_name=character,
                description=None,
            )
            db.add(role)
            added += 1

    db.commit()
    db.close()

    print(f" Đã thêm {added} vai diễn mới.")
    print(f" Bỏ qua {skipped} phim không có ID.")
    print(" Hoàn tất nạp dữ liệu vai diễn.")


if __name__ == "__main__":
    sync_roles()
