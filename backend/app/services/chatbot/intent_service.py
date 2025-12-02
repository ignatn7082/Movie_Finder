import re
from app.utils.text_utils import normalize_text

def detect_intent(prompt: str) -> str:
    p = normalize_text(prompt)
    
    if any(k in p for k in ["tom tat", "noi dung", "gioi thieu phim", "review", "danh gia"]):
        return "summary"
    if re.search(r"(dien vien|nhan vat|vai dien)\s+trong\s+phim", p):
        return "cast_role"
    if any(k in p for k in ["dien vien", "phim cua", "ai dong", "ai đóng"]):
        return "actor"
    if any(k in p for k in ["dao dien", "dao diễn", "đạo diễn"]):
        return "director"
    if re.search(r"(goi y|de xuat|muon xem)\s+phim\s+(hanh dong|hai|kinh di|tinh cam|hoat hinh)", p):
        return "recommend_genre"
    if any(k in p for k in ["goi y", "de xuat", "nen xem", "phim hay"]):
        return "recommend_general"
    return "general"