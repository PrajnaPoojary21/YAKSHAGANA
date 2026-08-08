# from dataset_loader import load_dataset, build_or_load_index, get_model

# _df = None
# _index = None

# def _ensure_loaded():
#     global _df, _index
#     if _df is None:
#         _df = load_dataset()
#         _index = build_or_load_index(_df)

# def find_best_match(transcribed_text, top_k=1):
#     _ensure_loaded()
#     model = get_model()

#     query_embedding = model.encode([transcribed_text], convert_to_numpy=True).astype("float32")
#     distances, indices = _index.search(query_embedding, top_k)

#     best_idx = indices[0][0]
#     best_row = _df.iloc[best_idx]

#     return {
#         "matched_padya": best_row["padya"],
#         "summary": best_row["summary"],
#         "distance": float(distances[0][0])   # lower = better match
#     }


from dataset_loader import load_dataset, build_or_load_index, get_model

_df = None
_index = None

def _ensure_loaded():
    global _df, _index
    if _df is None:
        _df = load_dataset()
        _index = build_or_load_index(_df)

def find_best_match(transcribed_text, top_k=1):
    _ensure_loaded()
    model = get_model()

    query_embedding = model.encode([transcribed_text], convert_to_numpy=True).astype("float32")
    distances, indices = _index.search(query_embedding, top_k)

    best_idx = indices[0][0]
    best_row = _df.iloc[best_idx]

    return {
        "matched_padya": best_row["padya_cleaned"],   # CHANGED: was best_row["padya"]
        "summary": best_row["summary"],
        "distance": float(distances[0][0])   # lower = better match
    }