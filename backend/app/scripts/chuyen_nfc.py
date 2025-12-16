#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script chuẩn hoá tên trong actor_labels.json (hoặc file json bất kỳ).
- Normalize Unicode về NFC
- Thay "_" bằng " " (tuỳ chọn)
- Tạo backup tự động trước khi ghi đè
- Hỗ trợ nested structures (list/dict/str)
"""

import json
import unicodedata
from pathlib import Path
from datetime import datetime
import sys

# ====== Cấu hình ======
INPUT_PATH = Path(r"F:\LV\ui\backend\data\actor_all_labels.json")   # đổi theo file của bạn
MAKE_BACKUP = True
REPLACE_UNDERSCORE = True   # nếu muốn thay "_" -> " "
LOWERCASE_KEYS = False      # nếu muốn chuyển thành lowercase khi normalize keys/values
# ======================


def normalize_text(s: str) -> str:
    if s is None:
        return s
    if not isinstance(s, str):
        s = str(s)
    # Compose characters to NFC so 'N̂guyễn' -> 'Nguyễn'
    s_norm = unicodedata.normalize("NFC", s)
    if REPLACE_UNDERSCORE:
        s_norm = s_norm.replace("_", " ")
    if LOWERCASE_KEYS:
        s_norm = s_norm.lower()
    # Trim spaces
    s_norm = s_norm.strip()
    return s_norm


def normalize_structure(obj):
    """
    Recursively normalize all string values in nested JSON-like structures.
    Returns tuple (normalized_obj, changed_count)
    """
    changed = 0

    if isinstance(obj, str):
        new = normalize_text(obj)
        if new != obj:
            return new, 1
        return new, 0

    if isinstance(obj, list):
        new_list = []
        for v in obj:
            nv, c = normalize_structure(v)
            changed += c
            new_list.append(nv)
        return new_list, changed

    if isinstance(obj, dict):
        new_dict = {}
        for k, v in obj.items():
            # optionally normalize key as well (if you need)
            new_k = normalize_text(k) if LOWERCASE_KEYS else k
            nv, c = normalize_structure(v)
            changed += c
            # If key normalization causes duplicate keys, keep the last one (user should check)
            new_dict[new_k] = nv
        return new_dict, changed

    # other primitive types (int/float/bool/None)
    return obj, 0


def main(input_path: Path):
    if not input_path.exists():
        print(f"[ERROR] File không tồn tại: {input_path}")
        sys.exit(1)

    # Load file
    try:
        raw = json.loads(input_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[ERROR] Không thể đọc file JSON: {e}")
        sys.exit(1)

    # Backup
    if MAKE_BACKUP:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = input_path.with_suffix(input_path.suffix + f".bak.{ts}")
        input_path.replace(backup_path)
        # write original back to original filename so we can operate on it (preserve original content)
        backup_path.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[INFO] Backup lưu tại: {backup_path}")

        # reload from backup variable `raw` (we already have it)
    print("[INFO] Bắt đầu chuẩn hoá...")

    normalized, changes = normalize_structure(raw)

    if changes == 0:
        # nếu không có thay đổi, phục hồi backup name -> original (nếu backup created)
        print("[INFO] Không phát hiện thay đổi nào (các chuỗi đã ở dạng NFC).")
        # nếu bạn tạo backup bằng replace, cần ghi lại raw vào file gốc
        input_path.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[INFO] Ghi lại file gốc (không thay đổi): {input_path}")
        return

    # Ghi file normalized ra file gốc
    try:
        input_path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"[ERROR] Không thể ghi file mới: {e}")
        # cố gắng khôi phục backup
        if MAKE_BACKUP and backup_path.exists():
            backup_path.replace(input_path)
            print("[WARN] Đã phục hồi file gốc từ backup.")
        sys.exit(1)

    print(f"[DONE] Chuẩn hoá xong. Tổng chuỗi thay đổi: {changes}")
    print(f"[INFO] File đã được ghi đè: {input_path}")
    if MAKE_BACKUP:
        print(f"[INFO] Backup vẫn nằm ở: {backup_path}")


if __name__ == "__main__":
    # cho phép truyền tên file từ CLI
    if len(sys.argv) > 1:
        INPUT_PATH = Path(sys.argv[1])
    main(INPUT_PATH)
