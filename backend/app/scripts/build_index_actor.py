# =================== CONFIG ===================

import timm
import torch
import torchvision.transforms as T
from PIL import Image, UnidentifiedImageError
import numpy as np
import os, json
from tqdm import tqdm
import faiss
from facenet_pytorch import MTCNN


MAX_SIZE = 1024
ACTOR_DIR = r"F:\ctu.bt\actor_avatar\actor_avatar"
OUTPUT_BASE = "index"

OUT_INDEX = os.path.join(OUTPUT_BASE, "actor_index_vit_colab.index")
OUT_LABELS = os.path.join(OUTPUT_BASE, "actor_labels_vit_colab.json")
OUT_META = os.path.join(OUTPUT_BASE, "actor_meta_vit_colab.json")
CENTROIDS_DIR = os.path.join(OUTPUT_BASE, "actor_centroids")
PROCESSED_FILE = os.path.join(OUTPUT_BASE, "processed_actors_vit_colab.json")

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print(f"[CONFIG] Using device: {DEVICE}")

# =================== LOAD MODEL ViT ===================


MODEL_NAME = "vit_base_patch16_224"
model = timm.create_model(MODEL_NAME, pretrained=True)
model.eval().to(DEVICE)
for p in model.parameters():
    p.requires_grad = False
EMBED_DIM = model.num_features
print("[INFO] ViT embedding dim:", EMBED_DIM)

# Preprocess ViT
preprocess = T.Compose([
    T.Resize((224,224)),
    T.ToTensor(),
    T.Normalize([0.5]*3,[0.5]*3)
])

# MTCNN Face Detector
mtcnn = MTCNN(keep_all=True, device=DEVICE)

# =================== UTILS ===================
def safe_load_image(path):
    try:
        img = Image.open(path).convert("RGB")
    except Exception as e:
        print(f"[SKIP] {path} → {e}")
        return None
    w,h = img.size
    if max(w,h) > MAX_SIZE:
        scale = MAX_SIZE / max(w,h)
        img = img.resize((int(w*scale), int(h*scale)), Image.LANCZOS)
    return img

def detect_face(img_path):
    img = safe_load_image(img_path)
    if img is None: return None
    try:
        boxes, probs = mtcnn.detect(img)
        if boxes is None or len(boxes)==0: return None
        biggest = int(np.argmax(probs))
        w,h = img.size
        x1,y1,x2,y2 = boxes[biggest].astype(int)
        x1,y1 = max(0,x1), max(0,y1)
        x2,y2 = min(w,x2), min(h,y2)
        if x2<=x1 or y2<=y1: return None
        return img.crop((x1,y1,x2,y2))
    except: return None

def extract_feature(img_pil):
    try:
        img_tensor = preprocess(img_pil).unsqueeze(0).to(DEVICE)
        with torch.amp.autocast("cuda", enabled=(DEVICE=="cuda")), torch.no_grad():
            feat = model.forward_features(img_tensor)
            if feat.ndim==3: feat = feat[:,0,:]  # CLS token
        feat = feat.cpu().numpy().flatten()
        return feat / (np.linalg.norm(feat)+1e-8)
    except:
        return None

def safe_name(name):
    s = name.replace(" ","_")
    for c in ('/', '\\', ':', '*', '?', '"', '<', '>', '|'): s = s.replace(c,"")
    return s.strip()

# =================== MAIN ===================
os.makedirs(OUTPUT_BASE, exist_ok=True)
os.makedirs(CENTROIDS_DIR, exist_ok=True)

# load processed actors
if os.path.exists(PROCESSED_FILE):
    with open(PROCESSED_FILE,"r",encoding="utf-8") as f: processed=set(json.load(f))
else: processed=set()

# load existing meta
if os.path.exists(OUT_META):
    with open(OUT_META,"r",encoding="utf-8") as f: meta_list=json.load(f)
else: meta_list=[]

actor_names = sorted(os.listdir(ACTOR_DIR)) if os.path.isdir(ACTOR_DIR) else []
print(f"Tổng diễn viên: {len(actor_names)}")

for actor in tqdm(actor_names, desc="Processing Actors"):
    actor_path = os.path.join(ACTOR_DIR, actor)
    if not os.path.isdir(actor_path): continue
    if actor in processed: continue

    image_files = [f for f in os.listdir(actor_path) if f.lower().endswith((".jpg",".png",".jpeg"))]
    feats=[]
    skipped=0
    processed_count=0

    for img_name in image_files:
        img_path = os.path.join(actor_path,img_name)
        face = detect_face(img_path)
        if face is None: skipped+=1; continue
        feat = extract_feature(face)
        if feat is None: skipped+=1; continue
        feats.append(feat); processed_count+=1

    if not feats:
        processed.add(actor)
        meta_list.append({"actor":actor,"images_processed":0,"images_skipped":skipped})
        with open(PROCESSED_FILE,"w",encoding="utf-8") as f: json.dump(list(processed),f,ensure_ascii=False,indent=2)
        with open(OUT_META,"w",encoding="utf-8") as f: json.dump(meta_list,f,ensure_ascii=False,indent=2)
        continue

    feats = np.array(feats).astype("float32")
    centroid = np.mean(feats,axis=0)
    centroid /= np.linalg.norm(centroid)+1e-8

    safe_actor = safe_name(actor)
    np.save(os.path.join(CENTROIDS_DIR,safe_actor+".npy"),centroid)

    meta_list.append({"actor":actor,"images_processed":processed_count,"images_skipped":skipped})
    processed.add(actor)
    with open(PROCESSED_FILE,"w",encoding="utf-8") as f: json.dump(list(processed),f,ensure_ascii=False,indent=2)
    with open(OUT_META,"w",encoding="utf-8") as f: json.dump(meta_list,f,ensure_ascii=False,indent=2)

# =================== BUILD FAISS INDEX ===================
centroid_files = sorted([f for f in os.listdir(CENTROIDS_DIR) if f.endswith(".npy")])
if not centroid_files:
    print("No centroids found, aborting.")
else:
    centroids=[]
    labels=[]
    for fn in centroid_files:
        c = np.load(os.path.join(CENTROIDS_DIR,fn))
        centroids.append(c)
        labels.append(os.path.splitext(fn)[0].replace("_"," "))

    centroids=np.array(centroids).astype("float32")
    index = faiss.IndexFlatIP(centroids.shape[1])
    index.add(centroids)

    faiss.write_index(index, OUT_INDEX)
    with open(OUT_LABELS,"w",encoding="utf-8") as f: json.dump(labels,f,ensure_ascii=False,indent=2)

    print("🎉 Actor index (ViT) build completed!")
    print(f"Total actors: {len(labels)}")
    print(f"Index saved to: {OUT_INDEX}")
