# import pandas as pd
# import numpy as np
# from sentence_transformers import SentenceTransformer
# import faiss
# import os

# DATASET_PATH = os.path.join(os.path.dirname(__file__), "dataset", "padya_dataset.csv")
# EMBEDDINGS_CACHE = os.path.join(os.path.dirname(__file__), "dataset", "padya_embeddings.npy")
# INDEX_CACHE = os.path.join(os.path.dirname(__file__), "dataset", "padya.index")

# _model = None

# def get_model():
#     global _model
#     if _model is None:
#         # multilingual model needed since your padya text is in Kannada
#         _model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
#     return _model

# def load_dataset():
#     df = pd.read_csv(DATASET_PATH)
#     df = df.dropna(subset=["padya"]).reset_index(drop=True)
#     return df

# def build_or_load_index(df):
#     model = get_model()

#     if os.path.exists(EMBEDDINGS_CACHE) and os.path.exists(INDEX_CACHE):
#         index = faiss.read_index(INDEX_CACHE)
#         return index

#     print(f"Embedding {len(df)} padyas... this runs once.")
#     embeddings = model.encode(
#         df["padya"].tolist(),
#         show_progress_bar=True,
#         convert_to_numpy=True
#     ).astype("float32")

#     np.save(EMBEDDINGS_CACHE, embeddings)

#     dim = embeddings.shape[1]
#     index = faiss.IndexFlatL2(dim)
#     index.add(embeddings)
#     faiss.write_index(index, INDEX_CACHE)

#     return index



import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import os

DATASET_PATH = os.path.join(os.path.dirname(__file__), "dataset", "padya_dataset.csv")
EMBEDDINGS_CACHE = os.path.join(os.path.dirname(__file__), "dataset", "padya_embeddings.npy")
INDEX_CACHE = os.path.join(os.path.dirname(__file__), "dataset", "padya.index")

_model = None

def get_model():
    global _model
    if _model is None:
        # multilingual model needed since your padya text is in Kannada
        _model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    return _model

def load_dataset():
    df = pd.read_csv(DATASET_PATH)
    # CHANGED: use padya_cleaned (OCR-error-corrected text) instead of the
    # original padya column, since that's the version with the safe fixes applied.
    df = df.dropna(subset=["padya_cleaned"]).reset_index(drop=True)
    return df

def build_or_load_index(df):
    model = get_model()

    if os.path.exists(EMBEDDINGS_CACHE) and os.path.exists(INDEX_CACHE):
        index = faiss.read_index(INDEX_CACHE)
        return index

    print(f"Embedding {len(df)} padya rows... this runs once.")
    embeddings = model.encode(
        df["padya_cleaned"].tolist(),   # CHANGED: was df["padya"]
        show_progress_bar=True,
        convert_to_numpy=True
    ).astype("float32")

    np.save(EMBEDDINGS_CACHE, embeddings)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    faiss.write_index(index, INDEX_CACHE)

    return index