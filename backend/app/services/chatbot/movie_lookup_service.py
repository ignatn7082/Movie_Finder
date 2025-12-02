from sqlalchemy.orm import Session
from app.models.movie import Movie
from app.models.role import Role
from app.services.base_service import STATIC_URL_PREFIX
from app.utils.fuzzy_matcher import fuzzy_find_best_match
from app.utils.text_utils import normalize_text

def _build_movie_dict(movie: Movie):
    poster = f"{STATIC_URL_PREFIX}{movie.posters}" if movie.posters else None
    return {
        "title": movie.title,
        "original_title": movie.original_title or movie.title,
        "overview": movie.overview or "Không có mô tả.",
        "release_date": movie.release_date,
        "director": movie.director,
        "stars": movie.stars,
        "genres_vn": movie.genres_vn,
        "poster": poster,
    }

def find_movie_by_title_fuzzy(db: Session, query: str) -> Movie | None:
    titles = [m.original_title or m.title for m in db.query(Movie.original_title, Movie.title).all()]
    best = fuzzy_find_best_match(query, titles, score_cutoff=80)
    if best:
        return db.query(Movie).filter(
            (Movie.original_title == best) | (Movie.title == best)
        ).first()
    return None

def lookup_cast_roles(db: Session, movie_name: str):
    movie = find_movie_by_title_fuzzy(db, movie_name)
    if not movie:
        return None, []
    
    roles = db.query(Role).filter(Role.movie_id == movie.id).all()
    role_list = [{"actor_name": r.actor_name, "role_name": r.role_name or "Chưa rõ"} for r in roles]
    return movie, role_list

def lookup_by_actor(db: Session, actor_query: str, top_k=10):
    actor_name = fuzzy_find_best_match(
        actor_query,
        [r[0] for r in db.query(Role.actor_name).distinct().all() if r[0]],
        score_cutoff=80
    )
    if not actor_name:
        return None, []
    
    roles = db.query(Role).join(Movie).filter(Role.actor_name.ilike(f"%{actor_name}%")).limit(top_k*2).all()
    seen = set()
    results = []
    for r in roles:
        m = r.movie
        if m.id in seen: continue
        seen.add(m.id)
        results.append(_build_movie_dict(m))
        if len(results) >= top_k: break
    return actor_name, results

def lookup_by_director(db: Session, director_query: str, top_k=10):
    director_name = fuzzy_find_best_match(
        director_query,
        [d[0] for d in db.query(Movie.director).distinct().all() if d[0]],
        score_cutoff=80
    )
    if not director_name:
        return None, []
    
    movies = db.query(Movie).filter(Movie.director.ilike(f"%{director_name}%")).limit(top_k).all()
    return director_name, [_build_movie_dict(m) for m in movies]