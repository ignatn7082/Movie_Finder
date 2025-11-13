import pandas as pd
import json
import os
from difflib import get_close_matches

# ===== Đường dẫn =====
CSV_PATH = r"F:\LV\ui\backend\data\Movies_vi_with_poster.csv"
ROLES_PATH = r"F:\LV\ui\backend\data\roles_updated.json"
OUTPUT_PATH = "roles_with_movie_id.json"
MISSING_LOG_PATH = "missing_roles.txt"


# ===== Đọc dữ liệu =====
# ========== Đọc dữ liệu ==========
df = pd.read_csv(CSV_PATH).fillna("")

# Ưu tiên sử dụng "Original Title" để ánh xạ
title_to_id = {}
for _, row in df.iterrows():
    original_title = str(row.get("Original Title", "")).strip().lower()
    if original_title:
        movie_id = int(row["id"]) if "id" in df.columns else int(_ + 1)
        title_to_id[original_title] = movie_id

print(f"🎬 Đã nạp {len(title_to_id)} tiêu đề gốc (Original Title) từ CSV.")

# ========== Đọc file vai trò ==========
with open(ROLES_PATH, "r", encoding="utf-8") as f:
    roles_data = json.load(f)

# ========== Hàm tìm movie_id theo original_title ==========
def find_movie_id_by_original(title: str):
    """So khớp theo Original Title (ưu tiên exact, fallback fuzzy)"""
    if not title:
        return None
    t = title.strip().lower()
    if t in title_to_id:
        return title_to_id[t]

    # Fuzzy match (cho phép gần đúng)
    matches = get_close_matches(t, list(title_to_id.keys()), n=1, cutoff=0.7)
    if matches:
        return title_to_id[matches[0]]
    return None


# ========== Ánh xạ movie_id ==========
updated_roles = []
missing_titles = []

for entry in roles_data:
    # Hỗ trợ cả entry là dict hoặc là string (chỉ chứa tiêu đề phim)
    if isinstance(entry, dict):
        movie_title = entry.get("movie_title") or entry.get("movie") or entry.get("title")
    elif isinstance(entry, str):
        movie_title = entry
        # chuyển string thành dict để xuất kết quả có movie_id
        entry = {"movie_title": movie_title}
    else:
        # bỏ qua kiểu dữ liệu lạ
        continue

    if not movie_title or not str(movie_title).strip():
        continue

    movie_title = str(movie_title).strip()
    movie_id = find_movie_id_by_original(movie_title)
    entry["movie_id"] = movie_id

    if not movie_id:
        missing_titles.append(movie_title)
    updated_roles.append(entry)

# ========== Xuất kết quả ==========
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(updated_roles, f, ensure_ascii=False, indent=2)

if missing_titles:
    with open(MISSING_LOG_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join([str(m) for m in missing_titles]))

print(f"✅ Hoàn tất ánh xạ movie_id cho {len(updated_roles)} vai trò.")
print(f"🎯 Tìm thấy {len(updated_roles) - len(missing_titles)} phim khớp.")
if missing_titles:
    print(f"⚠️ {len(missing_titles)} phim không tìm thấy (ghi log vào missing_roles.txt).")