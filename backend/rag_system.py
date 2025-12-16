"""
Simple RAG (Retrieval-Augmented Generation) System for GitHub Commits Dataset
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os


class GitHubCommitsRAG:
    def __init__(self, csv_path='github_commits_api.csv'):
        """Initialize the RAG system with the GitHub commits dataset."""
        self.csv_path = csv_path
        self.df = None
        self.vectorizer = None
        self.embeddings = None
        self.load_data()
    
    def load_data(self):
        """Load the CSV data."""
        print(f"Loading data from {self.csv_path}...")
        self.df = pd.read_csv(self.csv_path)
        print(f"Loaded {len(self.df)} commits")
        
        # Create a combined text field for better retrieval
        self.df['combined_text'] = (
            self.df['message'].fillna('') + ' ' + 
            self.df['author_name'].fillna('') + ' ' + 
            self.df['repo_name'].fillna('')
        )
    
    def train(self):
        """Train the RAG system by creating embeddings."""
        print("Training RAG system (creating embeddings)...")
        
        # Use TF-IDF for text vectorization
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Create embeddings
        self.embeddings = self.vectorizer.fit_transform(self.df['combined_text'])
        print(f"Created embeddings with shape: {self.embeddings.shape}")
    
    def retrieve(self, query, top_k=5):
        """Retrieve the most relevant commits based on the query."""
        if self.vectorizer is None or self.embeddings is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Transform query to embedding
        query_embedding = self.vectorizer.transform([query])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_embedding, self.embeddings).flatten()
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Return results
        results = []
        for idx in top_indices:
            results.append({
                'similarity': similarities[idx],
                'commit_sha': self.df.iloc[idx]['commit_sha'],
                'author': self.df.iloc[idx]['author_name'],
                'date': self.df.iloc[idx]['author_date'],
                'message': self.df.iloc[idx]['message'],
                'repo': self.df.iloc[idx]['repo_name'],
                'url': self.df.iloc[idx]['url']
            })
        
        return results
    
    def save_model(self, path='rag_model.pkl'):
        """Save the trained model."""
        model_data = {
            'vectorizer': self.vectorizer,
            'embeddings': self.embeddings,
            'df': self.df
        }
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"Model saved to {path}")
    
    def load_model(self, path='rag_model.pkl'):
        """Load a trained model."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file {path} not found")
        
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.vectorizer = model_data['vectorizer']
        self.embeddings = model_data['embeddings']
        self.df = model_data['df']
        print(f"Model loaded from {path}")
    
    def search(self, query, top_k=5):
        """Search and display results."""
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


def main():
    """Main function to demonstrate the RAG system."""
    # Initialize RAG system
    rag = GitHubCommitsRAG('github_commits_api.csv')
    
    # Train the system
    rag.train()
    
    # Save the model
    rag.save_model()
    
    # Example searches
    print("\n" + "="*80)
    print("RAG System Ready! Running example searches...")
    print("="*80)
    
    # Example 1: Search for debugging related commits
    rag.search("debug icons", top_k=3)
    
    # Example 2: Search for chat features
    rag.search("chat session", top_k=3)
    
    # Example 3: Search for specific author
    rag.search("Benjamin Pasero", top_k=3)


if __name__ == "__main__":
    main()
