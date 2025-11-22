import os
import json
import logging
from collections import defaultdict
from typing import Dict, Any, List, Tuple

import numpy as np
from PIL import Image, UnidentifiedImageError
from facenet_pytorch import MTCNN

# try cv2 for sharpness; fallback to simple gradient-based proxy
try:
    import cv2
    HAS_CV2 = True
except Exception:
    HAS_CV2 = False

# project imports (adjust if module path differs)
from app.db import SessionLocal
from app.models.role import Role

logger = logging.getLogger("select_rep_frames")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "..", "data"))
ROLES_MAP_PATH = os.path.join(DATA_DIR, "roles_with_movie_id.json")
OUT_PATH = os.path.join(DATA_DIR, "role_representative_frames.json")

mtcnn = MTCNN(keep_all=True, device=None)


def safe_open_image(path: str) -> Image.Image:
    try:
        img = Image.open(path).convert("RGB")
        return img
    except (UnidentifiedImageError, OSError) as e:
        logger.warning("Cannot open image %s: %s", path, e)
        return None


def compute_sharpness_np(img_gray: np.ndarray) -> float:
    # fallback sharpness estimate using gradient variance
    gy, gx = np.gradient(img_gray.astype(np.float32))
    grad_norm = np.sqrt(gx * gx + gy * gy)
    return float(np.var(grad_norm))


def score_frame(img_path: str) -> Tuple[float, Dict[str, Any]]:
    """Return (score, metadata). Higher = better."""
    meta = {"path": img_path, "face_prob": 0.0, "face_area_frac": 0.0, "sharpness": 0.0, "width": 0, "height": 0}
    img = safe_open_image(img_path)
    if img is None:
        return 0.0, meta

    w, h = img.size
    meta["width"], meta["height"] = w, h

    try:
        boxes, probs = mtcnn.detect(img)
    except Exception as e:
        logger.warning("MTCNN detect failed for %s: %s", img_path, e)
        boxes, probs = None, None

    face_prob = 0.0
    face_area_frac = 0.0
    sharpness = 0.0

    if boxes is not None and len(boxes) > 0:
        # choose largest by area
        areas = [(b[2] - b[0]) * (b[3] - b[1]) for b in boxes]
        idx = int(np.argmax(areas))
        face_prob = float(probs[idx]) if probs is not None else 0.0
        x1, y1, x2, y2 = boxes[idx].astype(int)
        face_w = max(1, x2 - x1)
        face_h = max(1, y2 - y1)
        face_area_frac = (face_w * face_h) / (w * h + 1e-9)

        # crop face for sharpness compute
        try:
            face_img = img.crop((x1, y1, x2, y2)).convert("L")
            arr = np.array(face_img)
            if HAS_CV2:
                sharpness = float(cv2.Laplacian(arr, cv2.CV_64F).var())
            else:
                sharpness = compute_sharpness_np(arr)
        except Exception as e:
            logger.debug("Sharpness calc failed for %s: %s", img_path, e)
            sharpness = 0.0
    else:
        # no face detected: use image-level proxies
        try:
            gray = img.convert("L")
            arr = np.array(gray)
            if HAS_CV2:
                sharpness = float(cv2.Laplacian(arr, cv2.CV_64F).var())
            else:
                sharpness = compute_sharpness_np(arr)
            # resolution score
            face_area_frac = min(1.0, (min(w, h) / 1024.0))
        except Exception:
            sharpness = 0.0

    meta.update({"face_prob": face_prob, "face_area_frac": face_area_frac, "sharpness": sharpness})

    # scoring heuristic: weight face prob most, then area fraction, then sharpness (scaled)
    score = face_prob * 0.6 + face_area_frac * 0.3 + (np.tanh(sharpness / 1000.0) * 0.1)
    # boost by resolution slightly
    score += min(0.05, (min(w, h) / 4096.0))
    return float(score), meta


def gather_role_frames_from_roles_map(roles_map: Dict[str, Any]) -> Dict[Tuple[str, str], List[str]]:
    """
    Return mapping (actor_key, role_name) -> [frame_paths...]
    actor_key prefers actor_id if available else actor_name
    roles_map entries expected: frame_id -> {actor_id, actor_name, role_name, movie_id, frame_path}
    """
    out = defaultdict(list)
    for fid, info in roles_map.items():
        frame_path = info.get("frame_path") or info.get("frame") or info.get("path")
        if not frame_path:
            continue
        # resolve absolute path if relative and data dir present
        if not os.path.isabs(frame_path):
            candidate = os.path.join(DATA_DIR, frame_path)
            if os.path.exists(candidate):
                frame_path = candidate
        actor_key = None
        if info.get("actor_id") is not None:
            actor_key = f"id:{info.get('actor_id')}"
        elif info.get("actor_name"):
            actor_key = f"name:{info.get('actor_name').strip()}"
        else:
            continue
        role_name = (info.get("role_name") or info.get("character") or "Unknown").strip()
        out[(actor_key, role_name)].append(frame_path)
    return out


def gather_role_frames_from_db() -> Dict[Tuple[str, str], List[str]]:
    out = defaultdict(list)
    try:
        session = SessionLocal()
        rows = session.query(Role).all()
        for r in rows:
            frame_path = getattr(r, "frame_path", None)
            if not frame_path:
                continue
            if not os.path.isabs(frame_path):
                candidate = os.path.join(DATA_DIR, frame_path)
                if os.path.exists(candidate):
                    frame_path = candidate
            actor_key = None
            if getattr(r, "actor_id", None) is not None:
                actor_key = f"id:{getattr(r, 'actor_id')}"
            else:
                actor_key = f"name:{(getattr(r, 'actor_name') or '').strip()}"
            role_name = (getattr(r, "role_name") or "Unknown").strip()
            out[(actor_key, role_name)].append(frame_path)
        session.close()
    except Exception as e:
        logger.exception("DB scan failed: %s", e)
    return out


def main():
    # load roles_map if exists
    roles_map = {}
    if os.path.exists(ROLES_MAP_PATH):
        try:
            with open(ROLES_MAP_PATH, "r", encoding="utf-8") as f:
                roles_map = json.load(f)
        except Exception as e:
            logger.warning("Failed load roles_map: %s", e)

    # collect candidates from roles_map + DB
    candidates = gather_role_frames_from_roles_map(roles_map)
    db_candidates = gather_role_frames_from_db()
    # merge
    for k, v in db_candidates.items():
        candidates[k].extend(v)

    logger.info("Total actor-role keys: %d", len(candidates))

    results = {}
    updated_roles_map = dict(roles_map)  # will add representative info if roles_map provided

    for (actor_key, role_name), frames in candidates.items():
        best_score = -1.0
        best_meta = None
        best_frame = None
        # remove duplicates and non-existing
        unique_frames = []
        for p in frames:
            if p and os.path.exists(p) and p not in unique_frames:
                unique_frames.append(p)
        if not unique_frames:
            continue

        for p in unique_frames:
            try:
                score, meta = score_frame(p)
            except Exception as e:
                logger.debug("score_frame failed for %s: %s", p, e)
                continue
            if score > best_score:
                best_score = score
                best_meta = meta
                best_frame = p

        if best_frame:
            actor_label = actor_key
            results.setdefault(actor_label, []).append({
                "role": role_name,
                "representative_frame": best_frame,
                "score": best_score,
                "meta": best_meta
            })

            # update roles_map entries that reference this frame_id (best-effort)
            # find frames in roles_map that match path and add rep info
            for fid, info in roles_map.items():
                path = info.get("frame_path") or info.get("frame") or info.get("path")
                if not path:
                    continue
                resolved = path
                if not os.path.isabs(resolved):
                    candidate = os.path.join(DATA_DIR, path)
                    if os.path.exists(candidate):
                        resolved = candidate
                if os.path.normpath(resolved) == os.path.normpath(best_frame):
                    info["representative_frame"] = best_frame
                    info["rep_score"] = best_score
                    updated_roles_map[fid] = info

    # save outputs
    try:
        with open(OUT_PATH + ".tmp", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        os.replace(OUT_PATH + ".tmp", OUT_PATH)
        logger.info("Saved representative frames to %s", OUT_PATH)
    except Exception as e:
        logger.exception("Failed to save %s: %s", OUT_PATH, e)

    # update roles_map file with rep info (optional)
    if roles_map:
        try:
            backup = ROLES_MAP_PATH + ".bak"
            if not os.path.exists(backup):
                with open(backup, "w", encoding="utf-8") as b:
                    json.dump(roles_map, b, ensure_ascii=False, indent=2)
            with open(ROLES_MAP_PATH + ".tmp", "w", encoding="utf-8") as f:
                json.dump(updated_roles_map, f, ensure_ascii=False, indent=2)
            os.replace(ROLES_MAP_PATH + ".tmp", ROLES_MAP_PATH)
            logger.info("Updated roles_map with representative_frame entries.")
        except Exception as e:
            logger.exception("Failed to update roles_map: %s", e)

    # summary
    total_roles = sum(len(v) for v in results.values())
    logger.info("Done. Representative frames selected for %d actor-roles (total roles: %d).", len(results), total_roles)


if __name__ == "__main__":
    main()