"""
Semantic Recall Layer

Uses sentence-transformers embeddings to pre-filter 100K candidates
to a manageable shortlist before full feature extraction.

Pre-computation is allowed — only the final ranking step is time-capped.
"""

import os
import json
import warnings
import numpy as np
from typing import List, Dict, Any, Optional

warnings.filterwarnings("ignore")

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False


def load_or_create_embeddings(
    candidates: List[Dict[str, Any]],
    cache_path: str
) -> Optional[np.ndarray]:
    """Load cached embeddings or compute new ones."""
    if os.path.exists(cache_path):
        print(f"  Loading cached embeddings from {cache_path}")
        return np.load(cache_path)

    if not HAS_SENTENCE_TRANSFORMERS:
        print("  sentence-transformers not available. Skipping semantic recall.")
        return None

    print("  Computing embeddings (this may take a few minutes)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    texts = []
    for cand in candidates:
        profile = cand.get("profile", {})
        title = profile.get("current_title", "")
        headline = profile.get("headline", "")
        summary = profile.get("summary", "")
        skills = [s.get("name", "") for s in cand.get("skills", [])]
        career_desc = " ".join(
            c.get("description", "") for c in cand.get("career_history", [])
        )

        text = f"{headline}. {summary}. Skills: {', '.join(skills)}. {career_desc}"
        texts.append(text[:500])  # Limit to 500 chars

    embeddings = model.encode(texts, show_progress_bar=True, batch_size=256)

    # Cache
    np.save(cache_path, embeddings)
    print(f"  Cached embeddings to {cache_path}")

    return embeddings


def compute_jd_embedding(jd_text: str, model) -> Optional[np.ndarray]:
    """Compute JD embedding."""
    if not jd_text or not model:
        return None
    return model.encode([jd_text])[0]


def semantic_recall(
    candidates: List[Dict[str, Any]],
    jd_text: str,
    data_dir: str,
    top_n: int = 3000
) -> List[int]:
    """
    Pre-filter candidates using semantic similarity to the JD.
    Returns indices of top-N candidates.
    """
    if not HAS_SENTENCE_TRANSFORMERS:
        return list(range(len(candidates)))

    cache_path = os.path.join(data_dir, "candidate_embeddings.npy")

    # Load or compute embeddings
    embeddings = load_or_create_embeddings(candidates, cache_path)
    if embeddings is None:
        return list(range(len(candidates)))

    # Compute JD embedding
    model = SentenceTransformer("all-MiniLM-L6-v2")
    jd_embedding = compute_jd_embedding(jd_text, model)
    if jd_embedding is None:
        return list(range(len(candidates)))

    # Compute similarities
    from sklearn.metrics.pairwise import cosine_similarity
    sims = cosine_similarity([jd_embedding], embeddings)[0]

    # Get top N
    top_indices = np.argsort(sims)[::-1][:top_n]
    print(f"  Semantic recall: {top_n} candidates selected from {len(candidates)}")

    return top_indices.tolist()
