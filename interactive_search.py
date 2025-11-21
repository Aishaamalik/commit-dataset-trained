"""
Interactive search interface for the GitHub Commits RAG system
"""

from rag_system import GitHubCommitsRAG
import os


def interactive_mode():
    """Run interactive search mode."""
    print("="*80)
    print("GitHub Commits RAG System - Interactive Mode")
    print("="*80)
    
    # Initialize RAG
    rag = GitHubCommitsRAG('github_commits_api.csv')
    
    # Check if model exists
    if os.path.exists('rag_model.pkl'):
        print("\nLoading existing model...")
        rag.load_model()
    else:
        print("\nNo existing model found. Training new model...")
        rag.train()
        rag.save_model()
    
    print("\nRAG system ready!")
    print("\nCommands:")
    print("  - Type your search query to find relevant commits")
    print("  - Type 'quit' or 'exit' to exit")
    print("  - Type 'stats' to see dataset statistics")
    print("-"*80)
    
    while True:
        query = input("\nEnter search query: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if query.lower() == 'stats':
            print(f"\nDataset Statistics:")
            print(f"Total commits: {len(rag.df)}")
            print(f"Unique authors: {rag.df['author_name'].nunique()}")
            print(f"Unique repos: {rag.df['repo_name'].nunique()}")
            print(f"Date range: {rag.df['author_date'].min()} to {rag.df['author_date'].max()}")
            continue
        
        if not query:
            print("Please enter a valid query.")
            continue
        
        # Perform search
        rag.search(query, top_k=5)


if __name__ == "__main__":
    interactive_mode()
