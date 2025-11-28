import os
import torch
import timm
import torchvision.transforms as T
from app.services.base_service import safe_load_image

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
DATA_DIR = os.path.join(BASE_DIR, "data")

LOCAL_MODEL_PATH = os.path.join(DATA_DIR, "vit_base_patch16_224.pth")
MODEL_NAME = "vit_base_patch16_224"

vit_model = None

# -------------------------------------------------
# Preprocess chuẩn cho ViT timm (224)
# -------------------------------------------------
vit_preprocess = T.Compose([
    T.Resize(256),
    T.CenterCrop(224),
    T.ToTensor(),
    T.Normalize(
        mean=[0.5, 0.5, 0.5],
        std=[0.5, 0.5, 0.5]
    )
])

# ===========================
# Load ViT model
# ===========================
try:
    print(f"[VIT] DEVICE: {DEVICE}")
    print(f"[VIT] Checking local model at: {LOCAL_MODEL_PATH}")

    if os.path.exists(LOCAL_MODEL_PATH):
        print(f"[VIT] Loading ViT weights from local file: {LOCAL_MODEL_PATH}")

        model = timm.create_model(MODEL_NAME, pretrained=False, num_classes=0)
        state = torch.load(LOCAL_MODEL_PATH, map_location=DEVICE)
        model.load_state_dict(state)

        vit_model = model.eval().to(DEVICE)

    else:
        print("[VIT] Local model not found. Loading pretrained model from timm...")
        model = timm.create_model(MODEL_NAME, pretrained=True, num_classes=0)
        vit_model = model.eval().to(DEVICE)

        print(f"[VIT] To save model locally:")
        print(f"torch.save(model.state_dict(), '{LOCAL_MODEL_PATH}')")

except Exception as e:
    print(f"[VIT ERROR] Failed to load model: {e}")
    vit_model = None


# ===========================
# Extract feature
# ===========================
@torch.no_grad()
def extract_feature(img_path):
    """Trả về vector đặc trưng (1,768) từ ViT timm."""
    try:
        if vit_model is None:
            print("[ERROR] ViT model not loaded.")
            return None

        # Load ảnh PIL
        img = safe_load_image(img_path)
        if img is None:
            return None

        # Preprocess → tensor
        img_tensor = vit_preprocess(img).unsqueeze(0).to(DEVICE)

        # Model forward (timm trả ra CLS vector sẵn)
        feat = vit_model(img_tensor)        # shape (1, 768)
        feat = feat.cpu().numpy()

        return feat

    except Exception as e:
        print(f"[ERROR] extract_feature: {e}")
        return None
