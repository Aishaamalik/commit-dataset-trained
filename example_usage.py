"""
Example usage of the AI Commit Message Generator
"""

from commit_generator import CommitMessageGenerator
import os

# Example 1: Basic usage with environment variable
def example_basic():
    """Generate commit message for staged changes."""
    print("Example 1: Basic Usage")
    print("-" * 50)
    
    generator = CommitMessageGenerator()
    result = generator.generate_commit_message()
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Commit Message:\n{result['commit_message']}\n")
        print(f"Files Changed: {len(result['analysis']['files_changed'])}")


# Example 2: Custom diff text
def example_custom_diff():
    """Generate commit message from custom diff."""
    print("\nExample 2: Custom Diff")
    print("-" * 50)
    
    custom_diff = """
diff --git a/app.py b/app.py
index 1234567..abcdefg 100644
--- a/app.py
+++ b/app.py
@@ -10,6 +10,12 @@ def main():
     print("Hello World")
+
+def new_feature():
+    '''Add new feature for user authentication'''
+    return authenticate_user()
+
 if __name__ == "__main__":
     main()
"""
    
    generator = CommitMessageGenerator()
    result = generator.generate_commit_message(diff_text=custom_diff)
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Commit Message:\n{result['commit_message']}")


# Example 3: With custom context
def example_with_context():
    """Generate commit message with additional context."""
    print("\nExample 3: With Custom Context")
    print("-" * 50)
    
    generator = CommitMessageGenerator()
    
    custom_context = """
Additional context: This change is part of a larger refactoring effort
to improve code maintainability and follows the team's new coding standards.
"""
    
    result = generator.generate_commit_message(custom_context=custom_context)
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Commit Message:\n{result['commit_message']}")


# Example 4: Programmatic usage
def example_programmatic():
    """Use the generator programmatically."""
    print("\nExample 4: Programmatic Usage")
    print("-" * 50)
    
    try:
        generator = CommitMessageGenerator()
        
        # Get git diff
        diff = generator.get_git_diff(staged=True)
        
        if not diff:
            print("No staged changes found")
            return
        
        # Analyze changes
        analysis = generator.analyze_changes(diff)
        print(f"Analysis: {analysis['files_changed']}")
        
        # Get similar commits
        similar = generator.get_similar_commits("fix bug in authentication", top_k=3)
        print(f"\nSimilar commits found: {len(similar)}")
        for commit in similar:
            print(f"  - {commit['message'][:60]}...")
        
        # Generate message
        result = generator.generate_commit_message()
        if "error" not in result:
            print(f"\nGenerated: {result['commit_message'][:100]}...")
    
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Check for API key
    if not os.getenv('GROQ_API_KEY'):
        print("⚠️  GROQ_API_KEY not set!")
        print("Set it with: export GROQ_API_KEY='your-key'")
        print("Get your key from: https://console.groq.com/\n")
    else:
        # Run examples
        try:
            example_basic()
            # example_custom_diff()
            # example_with_context()
            # example_programmatic()
        except Exception as e:
            print(f"\n❌ Error running examples: {e}")
