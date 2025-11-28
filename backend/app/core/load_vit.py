# import torch
# import timm
# import os

# MODEL_NAME = "vit_base_patch16_224"

# SAVE_PATH = "vit_base_patch16_224.pth"
# print("🔄 Downloading model:", MODEL_NAME)

# # Load pretrained từ internet (timm)
# model = timm.create_model(MODEL_NAME, pretrained=True, num_classes=0)

# # Lưu state_dict
# torch.save(model.state_dict(), SAVE_PATH)

# print("🎉 Saved:", SAVE_PATH)
