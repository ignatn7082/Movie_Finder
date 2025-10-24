import numpy as np
import cv2
from PIL import Image

def imread_unicode(path):
    """Đọc ảnh hỗ trợ đường dẫn Unicode"""
    stream = np.fromfile(path, dtype=np.uint8)
    return cv2.imdecode(stream, cv2.IMREAD_COLOR)

def normalize(vecs):
    """Chuẩn hoá vector"""
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    return vecs / norms

def load_image_for_clip(file, preprocess, device):
    """Mở ảnh và chuyển qua preprocessing của CLIP"""
    image = preprocess(Image.open(file)).unsqueeze(0).to(device)
    return image
