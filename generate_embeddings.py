"""Generate embeddings for the cleaned paper dataset.

This version is more robust and configurable:
- configurable input/output paths
- configurable model and batch size
- embeds title + abstract together for better retrieval quality
- stores a model name and combined text column for traceability
 - reuses cached embeddings from a previous run when the text and model match
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime
from typing import Dict, List

import pandas as pd
from sentence_transformers import SentenceTransformer


DEFAULT_MODEL = "all-MiniLM-L6-v2"


def make_embedding_key(text: str, model_name: str) -> str:
    digest = hashlib.sha256()
    digest.update(model_name.encode("utf-8"))
    digest.update(b"::")
    digest.update(text.encode("utf-8"))
    return digest.hexdigest()


def build_text(row: pd.Series, include_title: bool = True) -> str:
    title = str(row.get("title", "") or "").strip()
    abstract = str(row.get("abstract", "") or "").strip()
    parts = []
    if include_title and title:
        parts.append(title)
    if abstract:
        parts.append(abstract)
    return "\n".join(parts).strip()


def load_embedding_cache(path: str, model_name: str) -> Dict[str, List[float]]:
    if not os.path.exists(path):
        return {}

    try:
        cached_df = pd.read_csv(path)
    except Exception:
        return {}

    if "embedding_key" not in cached_df.columns or "embedding" not in cached_df.columns:
        return {}

    if "embedding_model" in cached_df.columns:
        cached_models = set(cached_df["embedding_model"].dropna().astype(str).unique().tolist())
        if cached_models and (len(cached_models) != 1 or model_name not in cached_models):
            return {}

    cache: Dict[str, List[float]] = {}
    for _, row in cached_df.iterrows():
        key = str(row.get("embedding_key", "") or "").strip()
        value = row.get("embedding", None)
        if not key or value is None:
            continue
        try:
            cache[key] = json.loads(value) if isinstance(value, str) else list(value)
        except Exception:
            continue
    return cache


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate sentence embeddings for cleaned papers")
    parser.add_argument("--input", default="dataset/clean_papers.csv")
    parser.add_argument("--output", default="dataset/clean_papers_with_embeddings.csv")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--include-title", action="store_true", help="Include title together with abstract in the embedding text")
    parser.add_argument("--max-rows", type=int, default=None, help="Optional limit for quick experiments")
    parser.add_argument("--no-cache", action="store_true", help="Do not reuse cached embeddings from the output file")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    if args.max_rows is not None:
        df = df.head(args.max_rows)

    print(f"Loaded papers: {len(df)} from {args.input}")

    if "abstract" not in df.columns:
        raise ValueError("Input file must contain an 'abstract' column")

    df["abstract"] = df["abstract"].fillna("").astype(str)
    if "title" not in df.columns:
        df["title"] = ""

    texts = [build_text(row, include_title=args.include_title) for _, row in df.iterrows()]
    df["embedding_text"] = texts
    df["embedding_key"] = [make_embedding_key(text, args.model) for text in texts]

    model = SentenceTransformer(args.model)

    cache: Dict[str, List[float]] = {}
    if not args.no_cache:
        cache = load_embedding_cache(args.output, args.model)

    embeddings: List[List[float] | None] = [None] * len(df)
    missing_texts = []
    missing_positions = []

    for idx, key in enumerate(df["embedding_key"].tolist()):
        cached = cache.get(key)
        if cached is not None:
            embeddings[idx] = cached
        else:
            missing_texts.append(texts[idx])
            missing_positions.append(idx)

    if missing_texts:
        print(f"Encoding {len(missing_texts)} new embeddings (cached {len(df) - len(missing_texts)})")
        encoded = model.encode(
            missing_texts,
            batch_size=args.batch_size,
            show_progress_bar=True,
            normalize_embeddings=True,
        )
        for pos, emb in zip(missing_positions, encoded):
            embeddings[pos] = emb.tolist()
    else:
        print("Reused embeddings from cache for all rows")

    if any(emb is None for emb in embeddings):
        raise RuntimeError("Some embeddings were not generated or loaded from cache")

    df["embedding"] = embeddings
    df["embedding_model"] = args.model
    df["embedding_created_at"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"

    df.to_csv(args.output, index=False)
    print(f"Embeddings generated with model '{args.model}'")
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()