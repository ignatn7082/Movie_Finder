import clip
import torch

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
clip_model, preprocess = clip.load("ViT-B/32", device=DEVICE)
clip_model.eval()

def tokenize_text(texts):
    """
    Wrapper an toàn để tokenize văn bản cho CLIP.
    Dù clip_model không có .tokenize, ta vẫn gọi được clip.tokenize().
    """
    try:
        return clip.tokenize(texts)
    except Exception as e:
        raise RuntimeError(f"Lỗi khi tokenize văn bản: {e}")

# Nếu có GPU thì dùng FP16 để tăng tốc
if torch.cuda.is_available():
    clip_model = clip_model.half()
