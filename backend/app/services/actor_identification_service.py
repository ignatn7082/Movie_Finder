import os
import json
import logging
import tempfile
import numpy as np
from typing import List, Dict, Any, Optional
from PIL import Image, UnidentifiedImageError
from facenet_pytorch import MTCNN
import faiss

from app.db import SessionLocal
from app.models.movie import Movie
from app.models.role import Role
# reuse your resnet extractor (adjust import if function name differs)
from app.services.resnet_service import extract_feature  # should accept PIL.Image and return 1D np.array

logger = logging.getLogger("actor_identify")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "..", "..", "data")
DATA_DIR = os.path.normpath(DATA_DIR)

# paths (adjust to your actual filenames)
ACTOR_INDEX_PATH = os.path.join(DATA_DIR, "actor_resnet50_face.index")
ACTOR_LABELS_PATH = os.path.join(DATA_DIR, "actor_resnet50_face_labels.npy")  # labels are frame ids (or similar)
ROLES_MAP_PATH = os.path.join(DATA_DIR, "roles_with_movie_id.json")  # mapping from frame id -> role info

# models
DEVICE = "cuda" if False else "cpu"  # MTCNN uses default device inside facenet_pytorch
mtcnn = MTCNN(keep_all=True, device=None)

# load FAISS index and labels
actor_index = None
actor_labels = None
if os.path.exists(ACTOR_INDEX_PATH):
    try:
        logger.info("Loading FAISS index %s", ACTOR_INDEX_PATH)
        actor_index = faiss.read_index(ACTOR_INDEX_PATH)
    except Exception as e:
        logger.exception("Failed to load actor index: %s", e)

if os.path.exists(ACTOR_LABELS_PATH):
    try:
        logger.info("Loading actor labels %s", ACTOR_LABELS_PATH)
        actor_labels = np.load(ACTOR_LABELS_PATH, allow_pickle=True).tolist()
    except Exception as e:
        logger.exception("Failed to load actor labels: %s", e)

# load roles mapping (frame -> {actor, role_name, movie_id, frame_path})
roles_map = {}
if os.path.exists(ROLES_MAP_PATH):
    try:
        with open(ROLES_MAP_PATH, "r", encoding="utf-8") as f:
            roles_map = json.load(f)
    except Exception as e:
        logger.exception("Failed to load roles map: %s", e)


def _detect_and_crop_face(p: str) -> Optional[Image.Image]:
    try:
        img = Image.open(p).convert("RGB")
    except (UnidentifiedImageError, Exception) as e:
        logger.warning("Cannot open image %s: %s", p, e)
        return None
    try:
        boxes, probs = mtcnn.detect(img)
    except Exception as e:
        logger.warning("mtcnn.detect failed for %s: %s", p, e)
        return None
    if boxes is None or len(boxes) == 0:
        return None
    # choose largest box
    try:
        areas = [(b[2] - b[0]) * (b[3] - b[1]) for b in boxes]
        idx = int(np.argmax(areas))
        x1, y1, x2, y2 = boxes[idx].astype(int)
        face = img.crop((x1, y1, x2, y2))
        return face
    except Exception as e:
        logger.warning("Failed to crop face %s: %s", p, e)
        return None


def identify_actor_from_upload(upload_path: str, top_k: int = 10) -> Dict[str, Any]:
    """
    Full pipeline:
    - detect face, extract resnet feature (V_query)
    - faiss search -> returns top_k frame ids
    - map frames -> actor ids/names and count frequency
    - fetch roles/movies for best actor and return list of movies with role + rep frame/poster
    """
    if actor_index is None or actor_labels is None:
        msg = "Actor FAISS index or labels not loaded"
        logger.warning(msg)
        return {"actor": None, "movies": [], "message": msg}

    face = _detect_and_crop_face(upload_path)
    if face is None:
        return {"actor": None, "movies": [], "message": "No face detected in input image"}

    # feature extraction (expects PIL.Image)
    feat = extract_feature(face)
    if feat is None:
        return {"actor": None, "movies": [], "message": "Feature extraction failed"}

    q = np.array(feat).astype("float32").reshape(1, -1)
    try:
        D, I = actor_index.search(q, top_k)
    except Exception as e:
        logger.exception("FAISS search failed: %s", e)
        return {"actor": None, "movies": [], "message": "FAISS search error"}

    frame_ids = []
    for idx in I[0]:
        try:
            label = actor_labels[int(idx)]
        except Exception:
            label = None
        if label is not None:
            frame_ids.append(str(label))

    if not frame_ids:
        return {"actor": None, "movies": [], "message": "No frames retrieved from index"}

    # Map frames -> actor candidates using roles_map or DB
    actor_counts = {}
    frame_to_role = {}  # keep one representative role/frame per frame
    for fid in frame_ids:
        info = roles_map.get(fid)
        if info:
            # expected keys: actor_name, actor_id, role_name, movie_id, frame_path
            actor_key = info.get("actor_name") or str(info.get("actor_id") or "")
            actor_counts[actor_key] = actor_counts.get(actor_key, 0) + 1
            frame_to_role[fid] = info
        else:
            # fallback: try DB lookup for role by frame id
            try:
                session = SessionLocal()
                r = session.query(Role).filter(getattr(Role, "frame_id", None) == fid).first()
                if r:
                    actor_key = getattr(r, "actor_name", None) or str(getattr(r, "actor_id", None) or "")
                    actor_counts[actor_key] = actor_counts.get(actor_key, 0) + 1
                    frame_to_role[fid] = {
                        "actor_name": getattr(r, "actor_name", None),
                        "actor_id": getattr(r, "actor_id", None),
                        "role_name": getattr(r, "role_name", None),
                        "movie_id": getattr(r, "movie_id", None),
                        "frame_path": getattr(r, "frame_path", None),
                    }
                session.close()
            except Exception:
                try:
                    session.close()
                except Exception:
                    pass

    if not actor_counts:
        return {"actor": None, "movies": [], "message": "No actor mapping found for retrieved frames"}

    # choose best actor (highest count). tie-break by max similarity D (we can map)
    best_actor = max(actor_counts.items(), key=lambda x: x[1])[0]

    # collect all frames in roles_map for this actor -> get movie ids and roles
    movies_map = {}  # movie_id -> {title, poster, roles: set(), rep_frame}
    # scan roles_map for entries with actor_name == best_actor OR actor_id == best_actor
    for fid, info in frame_to_role.items():
        a_name = info.get("actor_name") or str(info.get("actor_id") or "")
        if a_name != best_actor:
            continue
        movie_id = info.get("movie_id") or info.get("movie") if False else None
        role_name = info.get("role_name") or info.get("character") or "Unknown"
        frame_path = info.get("frame_path") or info.get("frame") or None

        if movie_id is None:
            continue
        # fetch movie metadata from DB
        try:
            session = SessionLocal()
            mobj = session.get(Movie, int(movie_id))
            if mobj:
                title = getattr(mobj, "title", None) or getattr(mobj, "original_title", None) or ""
                poster = getattr(mobj, "poster", None)
                poster_url = f"/static/{poster}" if poster else None
            else:
                title = str(movie_id)
                poster_url = None
            session.close()
        except Exception:
            try:
                session.close()
            except Exception:
                pass
            title = str(movie_id)
            poster_url = None

        if movie_id not in movies_map:
            movies_map[movie_id] = {"title": title, "poster": poster_url, "roles": set(), "rep_frame": frame_path}
        movies_map[movie_id]["roles"].add(role_name)
        if movies_map[movie_id]["rep_frame"] is None and frame_path:
            movies_map[movie_id]["rep_frame"] = frame_path

    # build response list
    movies_out = []
    for mid, info in movies_map.items():
        movies_out.append({
            "movie_id": int(mid),
            "title": info["title"],
            "roles": list(info["roles"]),
            "poster": info["poster"],
            "representative_frame": info["rep_frame"],
        })

    return {"actor": best_actor, "movies": movies_out, "raw": {"frame_ids": frame_ids, "distances": D[0].tolist()} }