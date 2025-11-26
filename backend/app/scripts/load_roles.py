# import os
# import json
# from sqlalchemy.orm import Session
# from app.db import SessionLocal, Base, engine
# from app.models.role import Role

# DATA_DIR = os.path.join("data")
# ROLE_FILE = os.path.join(DATA_DIR, "roles_updated.json")
# ROLE_ID_FILE = os.path.join(DATA_DIR, "roles_with_movie_id.json")


# def sync_roles():
#     """Nạp dữ liệu vai diễn từ role.json và role_id.json vào CSDL"""
#     db: Session = SessionLocal()
#     Base.metadata.create_all(bind=engine)

#     # Đọc file JSON
#     if not os.path.exists(ROLE_FILE) or not os.path.exists(ROLE_ID_FILE):
#         print(" Thiếu file role.json hoặc role_id.json!")
#         return

#     with open(ROLE_FILE, "r", encoding="utf-8") as f:
#         roles_data = json.load(f)

#     with open(ROLE_ID_FILE, "r", encoding="utf-8") as f:
#         role_ids = json.load(f)

#     # Tạo dictionary {movie_title_lower: movie_id}
#     movie_id_map = {
#         item["movie_title"].strip().lower(): item["movie_id"]
#         for item in role_ids
#     }

#     # Xóa dữ liệu cũ
#     print("  Xóa dữ liệu cũ trong bảng roles...")
#     deleted = db.query(Role).delete()
#     db.commit()
#     print(f"→ Đã xóa {deleted} bản ghi cũ.\n")

#     added, skipped = 0, 0

#     # Duyệt từng phim trong role.json
#     for movie_title, role_info in roles_data.items():
#         movie_title_clean = movie_title.strip().lower()
#         movie_id = role_info.get("movie_id") or movie_id_map.get(movie_title_clean)

#         if not movie_id:
#             print(f" Không có movie_id cho '{movie_title}' — bỏ qua.")
#             skipped += 1
#             continue

#         for actor, character in role_info.items():
#             if actor == "movie_id":
#                 continue

#             role = Role(
#                 movie_id=movie_id,
#                 movie_title=movie_title,
#                 actor=actor,
#                 character_name=character,
#                 description=None,
#             )
#             db.add(role)
#             added += 1

#     db.commit()
#     db.close()

#     print(f" Đã thêm {added} vai diễn mới.")
#     print(f" Bỏ qua {skipped} phim không có ID.")
#     print(" Hoàn tất nạp dữ liệu vai diễn.")


# if __name__ == "__main__":
#     sync_roles()


import os
import json
from sqlalchemy.orm import Session
from app.db import SessionLocal, Base, engine
from app.models.role import Role

DATA_DIR = os.path.join("data")
# Chỉ sử dụng duy nhất file này
ROLE_FILE_ONLY = os.path.join(DATA_DIR, "roles_up_2.json") 


def sync_roles_from_single_file():
    """
    Nạp dữ liệu vai diễn từ roles_up_2.json vào CSDL. 
    Chỉ thêm mới, KHÔNG xóa dữ liệu cũ.
    """
    db: Session = SessionLocal()
    Base.metadata.create_all(bind=engine)

    # Đọc file JSON duy nhất
    if not os.path.exists(ROLE_FILE_ONLY):
        print(f" Thiếu file {ROLE_FILE_ONLY}!")
        return

    try:
        with open(ROLE_FILE_ONLY, "r", encoding="utf-8") as f:
            roles_data = json.load(f)
    except json.JSONDecodeError:
        print(f" Lỗi đọc/giải mã file JSON: {ROLE_FILE_ONLY}. Vui lòng kiểm tra định dạng file.")
        return

    print("  Đang tiến hành đồng bộ dữ liệu vai diễn từ roles_up_2.json (chỉ thêm mới)...")
    
    added_new, skipped_no_id, skipped_existing = 0, 0, 0

    # Duyệt từng phim
    for movie_title, role_info in roles_data.items():
        
        # Lấy movie_id trực tiếp từ dữ liệu role_info
        movie_id = role_info.get("movie_id")

        if not movie_id:
            # Phim không có ID sẽ bị bỏ qua
            skipped_no_id += 1
            continue

        for actor, character in role_info.items():
            if actor == "movie_id":
                continue

            # 1. KIỂM TRA VAI DIỄN ĐÃ TỒN TẠI CHƯA (Tránh trùng lặp)
            existing_role = db.query(Role).filter(
                Role.movie_id == movie_id,
                Role.actor == actor,
                Role.character_name == character
            ).first()

            if existing_role:
                skipped_existing += 1
                continue
                
            # 2. THÊM VAI DIỄN MỚI
            role = Role(
                movie_id=movie_id,
                movie_title=movie_title,
                actor=actor,
                character_name=character,
                description=None,
            )
            db.add(role)
            added_new += 1

    db.commit()
    db.close()

    print(f"→ Đã thêm {added_new} vai diễn mới.")
    print(f"→ Đã bỏ qua {skipped_existing} vai diễn đã tồn tại (trùng lặp).")
    print(f"→ Đã bỏ qua {skipped_no_id} phim không có ID.")
    print(" Hoàn tất nạp dữ liệu vai diễn.")


if __name__ == "__main__":
    sync_roles_from_single_file()