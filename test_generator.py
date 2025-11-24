"""
Test the commit message generator with a sample diff
"""

from commit_generator import CommitMessageGenerator
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def test_with_sample_diff():
    """Test the generator with a sample diff."""
    
    # Sample diff representing adding the RAG system
    sample_diff = """
diff --git a/commit_generator.py b/commit_generator.py
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/commit_generator.py
@@ -0,0 +1,50 @@
+import os
+from groq import Groq
+from rag_system import GitHubCommitsRAG
+
+class CommitMessageGenerator:
+    def __init__(self, groq_api_key=None):
+        self.api_key = groq_api_key or os.getenv('GROQ_API_KEY')
+        self.client = Groq(api_key=self.api_key)
+        self.rag = GitHubCommitsRAG('github_commits_api.csv')
+        
+    def generate_commit_message(self, diff_text=None):
+        # Analyze changes and generate message
+        pass

diff --git a/rag_system.py b/rag_system.py
index abcdefg..7890123 100644
--- a/rag_system.py
+++ b/rag_system.py
@@ -10,6 +10,12 @@ class GitHubCommitsRAG:
         self.embeddings = None
         self.load_data()
     
+    def train(self):
+        print("Training RAG system...")
+        self.vectorizer = TfidfVectorizer(max_features=1000)
+        self.embeddings = self.vectorizer.fit_transform(self.df['combined_text'])
+        print(f"Created embeddings with shape: {self.embeddings.shape}")
+    
     def retrieve(self, query, top_k=5):
         query_embedding = self.vectorizer.transform([query])
         similarities = cosine_similarity(query_embedding, self.embeddings).flatten()
"""
    
    print("="*80)
    print("Testing AI Commit Message Generator")
    print("="*80)
    
    # Check API key
    if not os.getenv('GROQ_API_KEY'):
        print("\n❌ Error: GROQ_API_KEY not found in environment")
        return
    
    print("\n✅ API Key found")
    print("\nInitializing generator...")
    
    try:
        generator = CommitMessageGenerator()
        print("✅ Generator initialized")
        
        print("\nGenerating commit message for sample diff...")
        print("-"*80)
        
        result = generator.generate_commit_message(diff_text=sample_diff)
        
        if "error" in result:
            print(f"\n❌ Error: {result['error']}")
            return
        
        print("\n" + "="*80)
        print("✅ GENERATED COMMIT MESSAGE:")
        print("="*80)
        print(result['commit_message'])
        
        print("\n" + "="*80)
        print("ANALYSIS:")
        print("="*80)
        print(f"Files changed: {len(result['analysis']['files_changed'])}")
        print(f"Lines added: +{result['analysis']['additions']}")
        print(f"Lines deleted: -{result['analysis']['deletions']}")
        
        print("\n" + "="*80)
        print("SIMILAR COMMITS USED FOR CONTEXT:")
        print("="*80)
        for i, commit in enumerate(result['similar_commits'], 1):
            print(f"\n{i}. Similarity: {commit['similarity']:.4f}")
            print(f"   {commit['message'][:100]}...")
        
        print("\n" + "="*80)
        print("✅ Test completed successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_with_sample_diff()
