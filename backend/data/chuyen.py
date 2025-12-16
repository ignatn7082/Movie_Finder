# import json
# import re

# FILE = "actor_all_labels.json"

# with open(FILE, "r", encoding="utf-8") as f:
#     labels = json.load(f)

# def clean_name(name: str) -> str:
#     # xóa: image 9.jpg (), image9.jpg, image 12.jpg ()
#     name = re.sub(r'image\s*\d+\.jpg\s*\(\)', '', name, flags=re.IGNORECASE)
#     name = re.sub(r'image\s*\d+\.jpg', '', name, flags=re.IGNORECASE)
#     return name.strip()

# labels = [clean_name(name) if isinstance(name, str) else name for name in labels]

# with open(FILE, "w", encoding="utf-8") as f:
#     json.dump(labels, f, ensure_ascii=False, indent=2)

# print("✅ Đã làm sạch toàn bộ actor_name")


import json
import re

FILE = "actor_all_labels.json"

with open(FILE, "r", encoding="utf-8") as f:
    labels = json.load(f)

def clean_name(name: str) -> str:
    # Xóa: (image 17.jpg), (image6.jpg), (IMAGE 3.JPG)
    name = re.sub(r'\s*\(\s*image\s*\d+\.jpg\s*\)', '', name, flags=re.IGNORECASE)
    return name.strip()

labels = [clean_name(name) if isinstance(name, str) else name for name in labels]

with open(FILE, "w", encoding="utf-8") as f:
    json.dump(labels, f, ensure_ascii=False, indent=2)

print("✅ Đã bỏ toàn bộ (image x.jpg)")
