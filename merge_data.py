"""Merge available source CSVs into a single final dataset.

This script will look for the following files and include those that exist:
 - dataset/pubmed.csv
 - dataset/pmc.csv
 - dataset/semantic_scholar.csv

It deduplicates by title (case-insensitive), drops empty abstracts, and
optionally trims to `--max-results` rows.
"""
from __future__ import annotations

import argparse
import os
from typing import Dict

import pandas as pd


SOURCES: Dict[str, str] = {
    "PubMed": "dataset/pubmed.csv",
    "PMC": "dataset/pmc.csv",
    "SemanticScholar": "dataset/semantic_scholar.csv",
}


def read_if_exists(path: str) -> pd.DataFrame | None:
    if not os.path.exists(path):
        return None
    try:
        return pd.read_csv(path)
    except Exception as e:
        print(f"Failed to read {path}: {e}")
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge paper CSVs into dataset/final_papers.csv")
    parser.add_argument("--max-results", type=int, dest="max_results", default=None, help="Trim final output to this many rows")
    parser.add_argument("--output", default="dataset/final_papers.csv")
    args = parser.parse_args()

    dfs = []
    for name, path in SOURCES.items():
        df = read_if_exists(path)
        if df is None:
            print(f"Source missing: {path} (skipping)")
            continue
        print(f"{name} papers: {len(df)} -- loaded from {path}")
        dfs.append(df)

    if not dfs:
        print("No source CSVs found. Exiting.")
        return

    all_papers = pd.concat(dfs, ignore_index=True)
    print("Before removing duplicates:", len(all_papers))

    # Deduplicate by title (case-insensitive) if present, else drop exact duplicates
    if "title" in all_papers.columns:
        all_papers["title_norm"] = all_papers["title"].astype(str).str.strip().str.lower()
        all_papers = all_papers.drop_duplicates(subset=["title_norm"])
        all_papers = all_papers.drop(columns=["title_norm"])
    else:
        all_papers = all_papers.drop_duplicates()

    print("After removing duplicates:", len(all_papers))

    # Drop rows without abstracts (empty or missing)
    if "abstract" in all_papers.columns:
        all_papers = all_papers.dropna(subset=["abstract"])
        all_papers = all_papers[all_papers["abstract"].astype(str).str.strip() != ""]
    else:
        print("Warning: 'abstract' column not found; no abstract filtering applied.")

    print("After removing empty abstracts:", len(all_papers))

    if args.max_results is not None:
        all_papers = all_papers.head(args.max_results)
        print(f"Trimmed to top {len(all_papers)} results (max-results={args.max_results})")

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    all_papers.to_csv(args.output, index=False)
    print(f"Saved {args.output} ({len(all_papers)} records)")


if __name__ == "__main__":
    main()