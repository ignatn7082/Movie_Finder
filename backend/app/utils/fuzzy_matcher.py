# pip install rapidfuzz
from rapidfuzz import process, fuzz
from app.utils.text_utils import normalize_text

def fuzzy_find_best_match(query: str, choices: list[str], score_cutoff=75) -> str | None:
    if not choices or not query:
        return None
    normalized_query = normalize_text(query)
    normalized_choices = [normalize_text(c) for c in choices]
    
    best_match, score, _ = process.extractOne(normalized_query, normalized_choices, scorer=fuzz.token_sort_ratio)
    return choices[normalized_choices.index(best_match)] if score >= score_cutoff else None