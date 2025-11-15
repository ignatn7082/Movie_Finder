import unicodedata
import re

def slugify_filename(filename: str) -> str:
    # Tách tên và phần mở rộng
    name, ext = filename.rsplit(".", 1)

    # Chuẩn hóa Unicode → loại bỏ dấu
    name = unicodedata.normalize("NFD", name)
    name = name.encode("ascii", "ignore").decode("utf-8")

    # Chuyển khoảng trắng → _
    name = re.sub(r"\s+", "_", name)

    # Chỉ giữ ký tự a-zA-Z0-9_
    name = re.sub(r"[^a-zA-Z0-9_]", "", name)

    return f"{name.lower()}.{ext.lower()}"
