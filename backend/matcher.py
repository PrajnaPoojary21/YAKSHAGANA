"""
matcher.py — FAISS-backed padya retrieval.

CHANGED for the confidence-validation module (see validator.py):
  - Added find_top_k_matches(): returns the top-k candidates instead of
    just the winner, each with a *real* cosine similarity computed from
    the stored embeddings (not inferred from the raw L2 number FAISS
    returns). validator.py needs top-2 to score how ambiguous a match is,
    and it needs a similarity metric it can trust the meaning of.
  - find_best_match() is kept as a thin backward-compatible wrapper so
    nothing outside this file breaks; new code should prefer
    find_top_k_matches().

Everything else (index building, dataset loading) is untouched — see
dataset_loader.py.
"""

import os
import numpy as np
from dataset_loader import load_dataset, build_or_load_index, get_model, EMBEDDINGS_CACHE

_df = None
_index = None
_embeddings = None  # (N, dim) float32 array, row i == embedding for _df.iloc[i]


def _ensure_loaded():
    global _df, _index, _embeddings
    # CHANGED: check _index too, not just _df. If build_or_load_index()
    # raised partway through a previous request, _df could already be set
    # while _index stayed None -- the old "if _df is None" check would then
    # skip retrying forever, and every future request would fail with a
    # confusing "'NoneType' object has no attribute 'search'" instead of
    # the real underlying error (network issue downloading the embedding
    # model, a bad CSV row, etc.).
    if _df is None or _index is None:
        df = load_dataset()
        index = build_or_load_index(df)
        _df = df
        _index = index
    if _embeddings is None:
        if os.path.exists(EMBEDDINGS_CACHE):
            _embeddings = np.load(EMBEDDINGS_CACHE)
        else:
            # This shouldn't normally happen: build_or_load_index() writes
            # the cache the first time it runs. If it's missing, we fall
            # back to an L2->cosine approximation inside find_top_k_matches,
            # which is only correct if the embeddings happen to be unit-norm.
            _embeddings = None


def _cosine_similarity(a, b):
    a_norm = np.linalg.norm(a)
    b_norm = np.linalg.norm(b)
    if a_norm == 0.0 or b_norm == 0.0:
        return 0.0
    return float(np.dot(a, b) / (a_norm * b_norm))


def find_top_k_matches(transcribed_text, top_k=5):
    """
    Returns up to top_k candidates for transcribed_text, most similar first:

        [{
            "rank": 1,
            "matched_padya": "...",
            "summary": "...",
            "distance": 12.34,          # raw FAISS L2 distance (debug only)
            "cosine_similarity": 0.91,  # in [-1, 1], use this for confidence
        }, ...]

    Use this (not find_best_match) for anything that needs to reason about
    match confidence — it's the only function here that returns more than
    the single winner.
    """
    _ensure_loaded()
    if _df is None or len(_df) == 0:
        return []

    model = get_model()
    query_embedding = model.encode([transcribed_text], convert_to_numpy=True).astype("float32")

    k = min(top_k, len(_df))
    distances, indices = _index.search(query_embedding, k)

    results = []
    for rank, idx in enumerate(indices[0]):
        if idx == -1:
            continue
        row = _df.iloc[idx]
        l2_distance = float(distances[0][rank])

        if _embeddings is not None:
            cosine_sim = _cosine_similarity(query_embedding[0], _embeddings[idx])
        else:
            # Fallback only — assumes embeddings were unit-normalized before
            # indexing, which is NOT guaranteed for SentenceTransformer output
            # unless normalize_embeddings=True was passed to model.encode().
            # Prefer fixing EMBEDDINGS_CACHE over relying on this branch.
            cosine_sim = max(0.0, 1.0 - (l2_distance / 2.0))

        results.append({
            "rank": rank + 1,
            "matched_padya": row["padya_cleaned"],
            "summary": row["summary"],
            "distance": l2_distance,
            "cosine_similarity": cosine_sim,
        })

    return results


def find_best_match(transcribed_text, top_k=1):
    """
    Backward-compatible: returns just the top-1 result in the old shape.
    Prefer find_top_k_matches() in new code — this can't support confidence
    validation because it throws away the top-2+ candidates.
    """
    matches = find_top_k_matches(transcribed_text, top_k=max(top_k, 1))
    if not matches:
        return None
    best = matches[0]
    return {
        "matched_padya": best["matched_padya"],
        "summary": best["summary"],
        "distance": best["distance"],
    }