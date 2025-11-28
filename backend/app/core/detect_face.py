import torch
from facenet_pytorch import MTCNN
from PIL import Image

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Khởi tạo MTCNN
mtcnn = MTCNN(keep_all=False, device=DEVICE)

def detect_and_crop_face(img_path):
    """
    Trả về ảnh khuôn mặt (PIL Image) hoặc None nếu không thấy.
    """
    try:
        img = Image.open(img_path).convert("RGB")

        # phát hiện face
        face = mtcnn(img)

        if face is None:
            return None  # không tìm thấy khuôn mặt nào

        # face: tensor CHW -> đổi về PIL cho preprocess ViT
        face_pil = Image.fromarray(
            (face.permute(1, 2, 0).cpu().numpy() * 255).astype("uint8")
        )

        return face_pil

    except Exception as e:
        print("[ERROR detect_and_crop_face]:", e)
        return None
