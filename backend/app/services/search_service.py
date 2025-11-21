# import os
# import numpy as np
# import torch
# import faiss
# import pandas as pd
# import json
# from PIL import Image
# from sentence_transformers import SentenceTransformer
# from sklearn.metrics.pairwise import cosine_similarity
# from app.core.clip_loader import clip_model, preprocess, DEVICE, tokenize_text
# from app.core.faiss_index import index as image_index, train_labels as image_labels
# from app.utils.data_utils import load_movie_metadata
# from app.db import SessionLocal
# from app.models.role import Role
# from app.models.movie import Movie
# from sqlalchemy import or_
# from facenet_pytorch import MTCNN
# from PIL import ImageFile

# mtcnn = MTCNN(keep_all=True, device=DEVICE)
# # =========================
# # CONFIG
# # =========================
# movie_df = load_movie_metadata()



# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# DATA_DIR = os.path.join(BASE_DIR, "../../data")
# STATIC_URL_PREFIX = "http://localhost:8000/static/"

# TEXT_INDEX_PATH = os.path.join(DATA_DIR, "text.index")
# TEXT_LABELS_PATH = os.path.join(DATA_DIR, "text_labels.npy")

# INDEX_PATH = os.path.join(DATA_DIR, "movie_text.index")
# LABELS_PATH = os.path.join(DATA_DIR, "movie_labels.npy")
# META_PATH = os.path.join(DATA_DIR, "movie_metadata.json")

# ACTOR_INDEX_PATH = os.path.join(DATA_DIR, "actor_index.index")
# ACTOR_LABELS_JSON = os.path.join(DATA_DIR, "actor_labels.json")

# actor_index = faiss.read_index(ACTOR_INDEX_PATH)

# with open(ACTOR_LABELS_JSON, "r", encoding="utf-8") as f:
#     raw_labels = json.load(f)

# # Loại bỏ .npy.tmp, .npy, .tmp
# actor_labels = [
#     lbl.replace(".npy.tmp", "").replace(".npy", "").replace(".tmp", "")
#     for lbl in raw_labels
# ]


# ImageFile.LOAD_TRUNCATED_IMAGES = True
# MAX_SIZE = 1024



# def safe_load_image(path):
#     try:
#         img = Image.open(path).convert("RGB")
#     except Exception:
#         return None

#     w, h = img.size
#     if max(w, h) > MAX_SIZE:
#         scale = MAX_SIZE / max(w, h)
#         img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

#     return img


# # Load index
# if os.path.exists(ACTOR_INDEX_PATH):
#     print("[ACTOR] Loading actor index...")
#     actor_index = faiss.read_index(ACTOR_INDEX_PATH)
# else:
#     print(" Không tìm thấy actor_clip.index")

# # Load labels từ JSON
# if os.path.exists(ACTOR_LABELS_JSON):
#     print("[ACTOR] Loading actor label JSON...")
#     with open(ACTOR_LABELS_JSON, "r", encoding="utf-8") as f:
#         actor_labels = json.load(f)  # MUST be list
# else:
#     print(" Không tìm thấy actor_labels.json")


# index = faiss.read_index(INDEX_PATH)
# labels = np.load(LABELS_PATH)
# metadata = json.load(open(META_PATH, "r", encoding="utf-8"))



# # =========================
# # Load thêm roles (diễn viên - vai diễn)
# # =========================
# ROLES_PATH = os.path.join(DATA_DIR, "roles_updated.json")
# roles_data = {}

# if os.path.exists(ROLES_PATH):
#     with open(ROLES_PATH, "r", encoding="utf-8") as f:
#         roles_data = json.load(f)
#     print(f"[INFO] Loaded {len(roles_data)} movies with role info")
# else:
#     print("[WARN] roles_updated.json not found → skipping actor-role search")


# # =========================
# # Load SentenceTransformer + FAISS text index
# # =========================
# print("[INFO] Loading SentenceTransformer model...")
# text_model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# print("[INFO] Loading FAISS text index...")
# text_index = faiss.read_index(TEXT_INDEX_PATH)
# text_labels = np.load(TEXT_LABELS_PATH, allow_pickle=True)


# # =========================
# # Lấy thông tin phim
# # =========================


# def get_movie_info(title_or_label: str):
#     """
#     Tìm thông tin phim theo tiêu đề hoặc nhãn huấn luyện.
#     Trả về: title, poster URL, overview, director, stars, genres, release_date.
#     """
#     try:
#         key = title_or_label.split("_by_")[0].replace("_", " ").strip().lower()
#         row = movie_df[movie_df["Original Title"].str.lower() == key]

#         if not row.empty:
#             record = row.iloc[0]

#             # Chuẩn hóa đường dẫn poster
#             poster_file = record.get("PosterFile", "")
#             if isinstance(poster_file, float) or not poster_file:
#                 poster_url = None
#             else:
#                 raw_path = poster_file.replace("\\", "/")
#                 abs_path = os.path.join(DATA_DIR, raw_path)
#                 poster_url = f"{STATIC_URL_PREFIX}{raw_path}" if os.path.exists(abs_path) else None


#             # Trích xuất thông tin chi tiết
#             return {
#                 "title": record.get("Title", ""),
#                 "original_title": record.get("Original Title", ""),
#                 "overview": record.get("Overview", ""),
#                 "release_date": record.get("Release Date", ""),
#                 "director": record.get("Director", ""),
#                 "stars": record.get("Stars", ""),
#                 "genres": record.get("Genres", ""),
#                 "poster": poster_url,
#             }

#     except Exception as e:
#         print(f"[WARN] Lookup lỗi cho '{title_or_label}': {e}")

#     # Nếu không tìm thấy
#     return {
#         "title": title_or_label,
#         "original_title": None,
#         "overview": None,
#         "release_date": None,
#         "director": None,
#         "stars": None,
#         "genres": None,
#         "poster": None,
#     }


# def search_by_actor_or_role_db(keyword: str):
#     """Tìm phim qua bảng roles trong database"""
#     db = SessionLocal()
#     keyword_lower = f"%{keyword.lower()}%"
#     roles = db.query(Role).join(Movie).filter(
#         Role.actor_name.ilike(keyword_lower) | Role.role_name.ilike(keyword_lower)
#     ).all()

#     results = []
#     for r in roles:
#         info = get_movie_info(r.movie.title)
#         info["matched_actor"] = r.actor_name
#         info["matched_role"] = r.role_name
#         info["similarity"] = 1.0
#         results.append(info)

#     db.close()
#     return results



# def get_actor_movies(actor_name: str):
#     """Lấy tất cả phim + vai diễn của diễn viên từ DB."""
#     db = SessionLocal()
#     rows = (
#         db.query(Role, Movie)
#         .join(Movie, Role.movie_id == Movie.id)
#         .filter(Role.actor_name.ilike(actor_name))
#         .all()
#     )
#     db.close()

#     return [
#         {
#             "movie_id": movie.id,
#             "title": movie.title,
#             "role_name": role.role_name,
#             "poster": movie.poster,
#             "release_date": movie.release_date,
#         }
#         for role, movie in rows
#     ]



# def identify_actor(img_path: str, threshold=0.25):
#     """Nhận diện diễn viên dựa vào ảnh."""
#     if actor_index is None:
#         return None, 0

#     feat = normalize(extract_feature(img_path).reshape(1, -1).astype("float32"))
#     D, I = actor_index.search(feat, 1)

#     sim = float(D[0][0])
#     idx = I[0][0]

#     if sim < threshold:
#         return None, sim

#     return actor_labels[idx], sim




# # =========================
# # Chuẩn hoá vector
# # =========================
# def normalize(vecs: np.ndarray):
#     norms = np.linalg.norm(vecs, axis=1, keepdims=True)
#     return vecs / (norms + 1e-8)


# # =========================
# # 1️ TRUY VẤN ẢNH (CLIP)
# # =========================
# def extract_feature(pil_img):
#     """
#     Nhận ảnh PIL và trả về vector CLIP (numpy).
#     """
#     image = preprocess(pil_img).unsqueeze(0).to(DEVICE)
#     with torch.no_grad():
#         feat = clip_model.encode_image(image)
#     return feat.cpu().numpy().flatten()

# def detect_face(img_path):
#     """
#     Trả về ảnh crop khuôn mặt (PIL.Image) hoặc None nếu không phát hiện mặt.
#     """
#     img = safe_load_image(img_path)
#     if img is None:
#         return None

#     boxes, probs = mtcnn.detect(img)
#     if boxes is None or len(boxes) == 0:
#         return None

#     # Lấy mặt có xác suất cao nhất
#     best_idx = np.argmax(probs)
#     x1, y1, x2, y2 = boxes[best_idx]

#     face = img.crop((x1, y1, x2, y2))
#     return face
    


# # def query_by_image(img_path: str, top_k: int = 5, threshold: float = 0.25):
# #     """
# #     Upload ảnh diễn viên → trả về:
# #     {
# #         "actor": "Tên diễn viên",
# #         "similarity": 0.81,
# #         "movies": [
# #             {"movie_id": 2, "title": "...", "role_name": "...", "poster": "..."},
# #             ...
# #         ]
# #     }
# #     """

# #     if actor_index is None or actor_labels is None:
# #         return {
# #             "actor": None,
# #             "movies": [],
# #             "message": "Actor index chưa được tải"
# #         }
    
# #     # Extract feature
# #     feat = normalize(extract_feature(img_path).reshape(1, -1).astype("float32"))
# #     D, I = actor_index.search(feat, top_k)
    
# #     best_actor = None
# #     best_sim = 0
    
# #     for sim, idx in zip(D[0], I[0]):
# #         if sim >= threshold:
# #             actor_name = actor_labels[idx]  # lấy từ JSON list
    
# #             if sim > best_sim:
# #                 best_sim = sim
# #                 best_actor = actor_name
    
# #     if not best_actor:
# #         return {
# #             "actor": None,
# #             "movies": [],
# #             "message": "Không nhận diện được diễn viên"
# #         }
    
# #     movies = get_actor_movies(best_actor)
    
# #     return {
# #         "actor": best_actor,
# #         "similarity": float(best_sim),
# #         "movies": movies
# #     }


# def query_by_image(img_path, top_k=5, threshold=0.25):
    
#     face = detect_face(img_path)
#     if face is None:
#         return {"actor": None, "movies": [], "message": "Không thấy mặt người"}

#     feat = extract_feature(face).astype("float32")
#     feat = feat.reshape(1, -1)
#     faiss.normalize_L2(feat)

#     D, I = actor_index.search(feat, top_k)

#     best_sim = float(D[0][0])
#     best_actor = actor_labels[I[0][0]]
#     best_actor = (
#         best_actor.replace(".npy.tmp", "")
#                   .replace(".npy", "")
#                   .replace(".tmp", "")
#     )

#     if best_sim < threshold:
#         return {"actor": None, "movies": [], "message": "Không nhận diện được"}

#     movies = get_actor_movies(best_actor)

#     return {
#         "actor": best_actor,
#         "similarity": best_sim,
#         "movies": movies
#     }


# # =========================
# # 2️ TRUY VẤN TEXT (SentenceTransformer)
# # =========================

# def query_by_text(description: str, top_k: int = 5, threshold: float = 0.25):
#     """Tìm phim dựa trên mô tả hoặc tên phim bằng SentenceTransformer."""
#     if not description or not description.strip():
#         return [{"title": "Mô tả trống", "poster": None, "similarity": None}]
    
#     try:
#         # Encode text
#         vec = text_model.encode([description], convert_to_numpy=True, normalize_embeddings=True).astype("float32")
        
#         # Tìm kiếm trong FAISS
#         D, I = text_index.search(vec, top_k)
#         results = []
#         for sim, idx in zip(D[0], I[0]):
#             if sim >= threshold:
#                 info = get_movie_info(text_labels[idx])
#                 info["similarity"] = float(sim)
#                 results.append(info)

#         if not results:
#             return [{"title": "Không tìm thấy phim phù hợp", "poster": None}]
#         return results

#     except Exception as e:
#         import traceback
#         print("====== [ERROR - query_by_text()] ======")
#         print(traceback.format_exc())
#         print("=======================================")
#         return [{"title": f"Lỗi xử lý: {str(e)}", "poster": None}]



# def query_by_text_chatbot(prompt: str, top_k: int = 5):
#     """
#     Tìm phim theo tên, mô tả, đạo diễn, diễn viên hoặc vai diễn.
#     Kết hợp dữ liệu JSON và FAISS fallback.
#     """
#     if not prompt or not prompt.strip():
#         return []

#     prompt_lower = prompt.lower()
#     results = []

#     #  Tìm trong roles_updated.json (ưu tiên)
#     role_matches = search_by_actor_or_role_db(prompt)
#     if role_matches:
#         print(f"[MATCH] Found {len(role_matches)} role-based results")
#         return role_matches

#     #  Tìm trong CSV (đạo diễn hoặc diễn viên)
#     direct_matches = movie_df[
#         movie_df["Director"].str.lower().str.contains(prompt_lower, na=False)
#         | movie_df["Stars"].str.lower().str.contains(prompt_lower, na=False)
#     ]

#     if not direct_matches.empty:
#         for _, row in direct_matches.iterrows():
#             results.append({
#                 "title": row.get("Title", ""),
#                 "original_title": row.get("Original Title", ""),
#                 "overview": row.get("Overview", ""),
#                 "release_date": row.get("Release Date", ""),
#                 "director": row.get("Director", ""),
#                 "stars": row.get("Stars", ""),
#                 "genres": row.get("Genres", ""),
#                 "poster": f"{STATIC_URL_PREFIX}{row['PosterFile']}" if isinstance(row["PosterFile"], str) else None,
#                 "similarity": 1.0,
#             })
#         return results

#     #  Nếu không có → fallback FAISS (semantic search)
#     try:
#         vec = text_model.encode([prompt], convert_to_numpy=True, normalize_embeddings=True)
#         D, I = text_index.search(vec.astype("float32"), top_k)
#         for dist, idx in zip(D[0], I[0]):
#             row = movie_df.iloc[idx]
#             results.append({
#                 "title": row.get("Title", ""),
#                 "original_title": row.get("Original Title", ""),
#                 "overview": row.get("Overview", ""),
#                 "release_date": row.get("Release Date", ""),
#                 "director": row.get("Director", ""),
#                 "stars": row.get("Stars", ""),
#                 "genres": row.get("Genres", ""),
#                 "poster": f"{STATIC_URL_PREFIX}{row['PosterFile']}" if isinstance(row["PosterFile"], str) else None,
#                 "similarity": float(dist),
#             })
#     except Exception as e:
#         print("[ERROR][query_by_text_chatbot]", e)

#     return results




# def suggest_popular_movies(n=5):
#     """Gợi ý ngẫu nhiên vài phim nổi bật"""
#     try:
#         top_movies = movie_df.sort_values(by="Vote Average", ascending=False).head(20)
#         sample = top_movies.sample(min(n, len(top_movies)))

#         suggestions = []
#         for _, row in sample.iterrows():
#             suggestions.append({
#                 "title": row.get("Title", ""),
#                 "original_title": row.get("Original Title", ""),
#                 "overview": row.get("Overview", "")[:120] + "...",
#                 "genres": row.get("Genres", ""),
#                 "director": row.get("Director", ""),
#                 "poster": f"{STATIC_URL_PREFIX}{row['PosterFile']}" if isinstance(row["PosterFile"], str) else None,
#             })
#         return suggestions
#     except Exception as e:
#         print("[WARN] suggest_popular_movies():", e)
#         return []


# def query_by_keyword(keyword: str, top_k: int = 5):
#     """
#     Tìm kiếm phim theo từ khóa (tên phim, diễn viên, nhân vật, đạo diễn, thể loại)
#     """
#     db = SessionLocal()
#     keyword = keyword.strip().lower()
#     results = []

#     try:
#         #  Tìm phim khớp trực tiếp trong Movie
#         movie_matches = db.query(Movie).filter(
#             or_(
#                 Movie.title.ilike(f"%{keyword}%"),
#                 Movie.original_title.ilike(f"%{keyword}%"),
#                 Movie.director.ilike(f"%{keyword}%"),
#                 Movie.stars.ilike(f"%{keyword}%"),
#                 Movie.genres.ilike(f"%{keyword}%"),
#                 Movie.overview.ilike(f"%{keyword}%"),
#             )
#         ).limit(top_k).all()

#         for m in movie_matches:
#             results.append({
#                 "title": m.title,
#                 "original_title": m.original_title,
#                 "overview": m.overview,
#                 "release_date": m.release_date,
#                 "director": m.director,
#                 "stars": m.stars,
#                 "genres": m.genres,
#                 "poster": f"http://localhost:8000/static/{m.poster}" if m.poster else None,
#                 "match_type": "movie",
#             })

#         # 2 Tìm trong bảng Role (actor_name hoặc role_name)
#         role_matches = db.query(Role).filter(
#             or_(
#                 Role.actor_name.ilike(f"%{keyword}%"),
#                 Role.role_name.ilike(f"%{keyword}%")
#             )
#         ).limit(top_k * 2).all()

#         for r in role_matches:
#             movie = db.query(Movie).filter(Movie.id == r.movie_id).first()
#             if movie:
#                 results.append({
#                     "title": movie.title,
#                     "original_title": movie.original_title,
#                     "actor": r.actor_name,
#                     "role": r.role_name,
#                     "poster": f"http://localhost:8000/static/{movie.poster}" if movie.poster else None,
#                     "match_type": "role",
#                 })

#     finally:
#         db.close()

#     #  Gộp kết quả & loại trùng
#     unique = {f"{r.get('title')}-{r.get('match_type')}": r for r in results}
#     return list(unique.values())[:top_k]