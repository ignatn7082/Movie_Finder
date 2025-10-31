# import os
# import clip
# import torch

# DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# # ưu tiên biến môi trường (đặt trong docker-compose.yml)
# DOWNLOAD_ROOT = os.getenv("CLIP_DOWNLOAD_ROOT", os.path.expanduser("~/.cache/clip"))
# os.makedirs(DOWNLOAD_ROOT, exist_ok=True)

# MODEL_NAME = "ViT-B/32"

# try:
#     # dùng download_root để tránh ghi vào default home cache nếu bạn mount khác
#     clip_model, preprocess = clip.load(MODEL_NAME, device=DEVICE, download_root=DOWNLOAD_ROOT)
# except Exception as e:
#     # fallback: nếu bạn đã lưu model file cụ thể, thử load từ file cục bộ
#     local_candidate = os.path.join(DOWNLOAD_ROOT, "models", "ViT-B-32.pt")
#     if os.path.exists(local_candidate):
#         clip_model, preprocess = clip.load(local_candidate, device=DEVICE)
#     else:
#         # nếu không có model, raise để log rõ nguyên nhân
#         raise RuntimeError(f"CLIP model load failed (tried {DOWNLOAD_ROOT}): {e}")

# clip_model.eval()

import os
import torch
import clip

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")

LOCAL_MODEL_PATH = os.path.join(DATA_DIR, "ViT-B-32.pt")
def tokenize_text(texts):
    if isinstance(texts, str):
        texts = [texts]
    return clip.tokenize(texts, truncate=True).to(DEVICE)

clip_model = None
preprocess = None

try:
    # Nếu đã có file local thì chỉ load
    if os.path.exists(LOCAL_MODEL_PATH):
        print(f" Loading CLIP model from local file: {LOCAL_MODEL_PATH}")
        model, preprocess = clip.load("ViT-B/32", device=DEVICE)
        state_dict = torch.load(LOCAL_MODEL_PATH, map_location=DEVICE)
        model.load_state_dict(state_dict)
        clip_model = model.eval().to(DEVICE)
    else:
        # Không có mạng, không tải được
        print(f" Không tìm thấy model {LOCAL_MODEL_PATH}.")
        print(" Vui lòng tải thủ công file ViT-B-32.pt và đặt tại app/data/")
        print("   Link download: https://openaipublic.azureedge.net/clip/models/ViT-B-32.pt")
        clip_model, preprocess = clip.load("ViT-B/32", device=DEVICE)
        clip_model = clip_model.eval().to(DEVICE)

except Exception as e:
    print(f" CLIP model load failed: {e}")
    print(" Hệ thống vẫn khởi động, nhưng chức năng search ảnh sẽ bị vô hiệu.")
    clip_model = None
    preprocess = None