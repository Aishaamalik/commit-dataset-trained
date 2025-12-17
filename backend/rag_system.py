"""
Simple RAG (Retrieval-Augmented Generation) System for a GitHub commits dataset.

This module builds a lightweight TF‑IDF based index over a CSV of historical
commits which can then be queried for similarity to a new change description.
"""

from __future__ import annotations

import os
import pickle
from typing import Dict, List

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class GitHubCommitsRAG:
    """
    Tiny RAG system backed by TF‑IDF vectors over commit text.
    """

    def __init__(self, csv_path: str = "github_commits_api.csv") -> None:
        """
        Prepare the RAG instance and load the underlying CSV file.
        """
        self.csv_path = csv_path
        self.df: pd.DataFrame | None = None
        self.vectorizer: TfidfVectorizer | None = None
        self.embeddings = None
        self.load_data()

    # ------------------------------------------------------------------ #
    # Data loading and training
    # ------------------------------------------------------------------ #

    def load_data(self) -> None:
        """
        Load the commit CSV and add a `combined_text` helper column.
        """
        print(f"Loading data from {self.csv_path}...")
        self.df = pd.read_csv(self.csv_path)
        print(f"Loaded {len(self.df)} commits")

        # Combine multiple text fields into a single search string
        self.df["combined_text"] = (
            self.df["message"].fillna("")
            + " "
            + self.df["author_name"].fillna("")
            + " "
            + self.df["repo_name"].fillna("")
        )

    def train(self) -> None:
        """
        Train the RAG system by creating TF‑IDF embeddings.
        """
        if self.df is None:
            raise ValueError("Dataframe is not loaded. Call load_data() first.")

        print("Training RAG system (creating embeddings)...")

        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words="english", ngram_range=(1, 2))
        self.embeddings = self.vectorizer.fit_transform(self.df["combined_text"])
        print(f"Created embeddings with shape: {self.embeddings.shape}")

    # ------------------------------------------------------------------ #
    # Retrieval
    # ------------------------------------------------------------------ #

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve the `top_k` most relevant commits for a text query.
        """
        if self.vectorizer is None or self.embeddings is None:
            raise ValueError("Model not trained. Call train() first.")

        query_embedding = self.vectorizer.transform([query])

        similarities = cosine_similarity(query_embedding, self.embeddings).flatten()

        top_indices = np.argsort(similarities)[-top_k:][::-1]

        results: List[Dict] = []
        for idx in top_indices:
            results.append(
                {
                    "similarity": float(similarities[idx]),
                    "commit_sha": self.df.iloc[idx]["commit_sha"],
                    "author": self.df.iloc[idx]["author_name"],
                    "date": self.df.iloc[idx]["author_date"],
                    "message": self.df.iloc[idx]["message"],
                    "repo": self.df.iloc[idx]["repo_name"],
                    "url": self.df.iloc[idx]["url"],
                }
            )

        return results

    # ------------------------------------------------------------------ #
    # Persistence helpers
    # ------------------------------------------------------------------ #

    def save_model(self, path: str = "rag_model.pkl") -> None:
        """
        Persist the trained vectorizer + embeddings + dataframe to disk.
        """
        model_data = {"vectorizer": self.vectorizer, "embeddings": self.embeddings, "df": self.df}
        with open(path, "wb") as f:
            pickle.dump(model_data, f)
        print(f"Model saved to {path}")

    def load_model(self, path: str = "rag_model.pkl") -> None:
        """
        Load a previously persisted model from disk.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file {path} not found")

        with open(path, "rb") as f:
            model_data = pickle.load(f)

        self.vectorizer = model_data["vectorizer"]
        self.embeddings = model_data["embeddings"]
        self.df = model_data["df"]
        print(f"Model loaded from {path}")

    # ------------------------------------------------------------------ #
    # Convenience CLI helpers
    # ------------------------------------------------------------------ #

    def search(self, query: str, top_k: int = 5):
        """
        Convenience helper that prints results to stdout for manual usage.
        """
        print(f"\nSearching for: '{query}'")
        print("-" * 80)

        results = self.retrieve(query, top_k)

        for i, result in enumerate(results, 1):
            print(f"\n{i}. Similarity: {result['similarity']:.4f}")
            print(f"   Author: {result['author']}")
            print(f"   Date: {result['date']}")
            print(f"   Repo: {result['repo']}")
            print(f"   Message: {result['message'][:100]}...")
            print(f"   URL: {result['url']}")

        return results


def main() -> None:
    """
    Example entry point to build and test the RAG model.
    """
    rag = GitHubCommitsRAG("github_commits_api.csv")

    rag.train()

    rag.save_model()

    print("\n" + "=" * 80)
    print("RAG System Ready! Running example searches...")
    print("=" * 80)

    rag.search("debug icons", top_k=3)
    rag.search("chat session", top_k=3)
    rag.search("Benjamin Pasero", top_k=3)


if __name__ == "__main__":
    main()

