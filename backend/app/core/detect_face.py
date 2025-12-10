import torch
from facenet_pytorch import MTCNN
from mtcnn import MTCNN as mtcnn_lib
from PIL import Image
from typing import Optional
import numpy as np
from io import BytesIO

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Khởi tạo MTCNN
mtcnn = MTCNN(keep_all=False, device=DEVICE)

def crop_face(pil_img: Image.Image):
    detector = mtcnn_lib()
    img_np = np.array(pil_img)

    results = detector.detect_faces(img_np)
    if len(results) == 0:
        print(" Không phát hiện khuôn mặt — dùng ảnh gốc.")
        return None
    
    best_face = max(results, key=lambda x: x['confidence'])
    x, y, w, h = best_face['box']

    x = max(0, x)
    y = max(0, y)

    face = pil_img.crop((x, y, x + w, y + h))
    print(f" Đã cắt khuôn mặt: box = {x, y, w, h}")
    face = face.resize((224, 224), Image.Resampling.LANCZOS)
    return face



# Khởi tạo global – siêu ổn định, chạy ngon trong Docker
_mtcnn = MTCNN(
    image_size=224,
    margin=40,
    min_face_size=40,
    thresholds=[0.6, 0.7, 0.7],
    factor=0.709,
    post_process=True,
    select_largest=True,
    keep_all=False,
    device='cuda' if torch.cuda.is_available() else 'cpu'
)

def detect_and_crop_face(
    image: Image.Image | str | bytes,
    target_size: tuple[int, int] = (224, 224),
    margin: int = 40
) -> Optional[Image.Image]:
    """
    Dùng facenet-pytorch MTCNN - chính xác, ổn định, không lỗi joblib
    """
    try:
        # 1. Chuẩn hóa input thành PIL.Image
        if isinstance(image, (str, bytes)):
            pil_img = Image.open(image if isinstance(image, str) else BytesIO(image))
        else:
            pil_img = image.copy() if isinstance(image, Image.Image) else image
        
        pil_img = pil_img.convert("RGB")

        # 2. Detect khuôn mặt – DÙNG BIẾN _mtcnn ĐÃ KHỞI TẠO
        boxes, probs = _mtcnn.detect(pil_img)

        if boxes is None or len(boxes) == 0:
            print("[DEBUG] MTCNN: Không phát hiện khuôn mặt")
            return None

        # Lấy khuôn mặt đầu tiên (đã select_largest=True)
        x1, y1, x2, y2 = boxes[0]
        confidence = probs[0]

        print(f"[DEBUG] Phát hiện khuôn mặt | confidence={confidence:.3f} | box=({x1:.0f},{y1:.0f},{x2:.0f},{y2:.0f})")

        # Thêm margin
        w, h = pil_img.size
        margin_px = margin
        crop_box = (
            max(0, int(x1) - margin_px),
            max(0, int(y1) - margin_px),
            min(w, int(x2) + margin_px),
            min(h, int(y2) + margin_px)
        )

        cropped = pil_img.crop(crop_box)
        cropped = cropped.resize(target_size, Image.Resampling.LANCZOS)

        return cropped

    except Exception as e:
        print(f"[ERROR] detect_and_crop_face: {e}")
        return None