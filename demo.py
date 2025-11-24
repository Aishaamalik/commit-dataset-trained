"""
Complete demo of the AI Commit Message Generator
"""

from commit_generator import CommitMessageGenerator
from dotenv import load_dotenv
import os

load_dotenv()

def demo():
    """Run a complete demo."""
    
    print("="*80)
    print("🤖 AI COMMIT MESSAGE GENERATOR DEMO")
    print("="*80)
    print("\nThis system uses:")
    print("  ✓ RAG (Retrieval-Augmented Generation) to learn from 1000+ commits")
    print("  ✓ Groq's LLaMA 3.3 70B model for intelligent generation")
    print("  ✓ Git diff analysis for context")
    print("="*80)
    
    if not os.getenv('GROQ_API_KEY'):
        print("\n❌ GROQ_API_KEY not found")
        return
    
    # Example diffs for different scenarios
    examples = [
        {
            "name": "Bug Fix",
            "diff": """
diff --git a/auth.py b/auth.py
index abc123..def456 100644
--- a/auth.py
+++ b/auth.py
@@ -15,7 +15,7 @@ def authenticate_user(username, password):
     user = db.get_user(username)
     if not user:
-        return None
+        return False
     
-    if user.password == password:
+    if bcrypt.checkpw(password.encode(), user.password):
         return user
"""
        },
        {
            "name": "New Feature",
            "diff": """
diff --git a/api.py b/api.py
new file mode 100644
index 0000000..abc123
--- /dev/null
+++ b/api.py
@@ -0,0 +1,25 @@
+from flask import Flask, jsonify
+
+app = Flask(__name__)
+
+@app.route('/api/users', methods=['GET'])
+def get_users():
+    '''Retrieve all users from database'''
+    users = User.query.all()
+    return jsonify([user.to_dict() for user in users])
+
+@app.route('/api/users/<int:id>', methods=['GET'])
+def get_user(id):
+    '''Retrieve a specific user by ID'''
+    user = User.query.get_or_404(id)
+    return jsonify(user.to_dict())
"""
        },
        {
            "name": "Refactoring",
            "diff": """
diff --git a/utils.py b/utils.py
index 111222..333444 100644
--- a/utils.py
+++ b/utils.py
@@ -5,15 +5,8 @@ import json
 
-def process_data(data):
-    result = []
-    for item in data:
-        if item['active']:
-            result.append(item)
-    return result
+def process_data(data):
+    return [item for item in data if item.get('active', False)]
"""
        }
    ]
    
    generator = CommitMessageGenerator()
    
    for i, example in enumerate(examples, 1):
        print(f"\n{'='*80}")
        print(f"EXAMPLE {i}: {example['name']}")
        print('='*80)
        
        result = generator.generate_commit_message(diff_text=example['diff'])
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            continue
        
        print(f"\n📝 Generated Message:")
        print("-"*80)
        print(result['commit_message'])
        
        print(f"\n📊 Analysis:")
        print(f"  • Files: {len(result['analysis']['files_changed'])}")
        print(f"  • Added: +{result['analysis']['additions']} lines")
        print(f"  • Deleted: -{result['analysis']['deletions']} lines")
        
        print(f"\n🔍 Similar Commits (for context):")
        for j, commit in enumerate(result['similar_commits'][:2], 1):
            print(f"  {j}. {commit['message'][:70]}...")
    
    print("\n" + "="*80)
    print("✅ DEMO COMPLETED!")
    print("="*80)
    print("\nTo use with your own repository:")
    print("  1. Stage your changes: git add .")
    print("  2. Run: python commit_generator.py")
    print("  3. Review and commit!")
    print("="*80)


if __name__ == "__main__":
    demo()
