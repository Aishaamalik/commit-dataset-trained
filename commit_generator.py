"""
AI Commit Message Generator using RAG + Groq LLM
Analyzes git diff and generates contextual commit messages
"""

import os
import subprocess
from groq import Groq
from rag_system import GitHubCommitsRAG
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class CommitMessageGenerator:
    def __init__(self, groq_api_key=None):
        """Initialize the commit message generator."""
        self.api_key = groq_api_key or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found. Set it as environment variable or pass it.")
        
        self.client = Groq(api_key=self.api_key)
        self.rag = GitHubCommitsRAG('github_commits_api.csv')
        
        # Load or train RAG model
        if os.path.exists('rag_model.pkl'):
            print("Loading RAG model...")
            self.rag.load_model()
        else:
            print("Training RAG model...")
            self.rag.train()
            self.rag.save_model()
    
    def get_git_diff(self, staged=True):
        """Get git diff from the current repository."""
        try:
            if staged:
                # Get staged changes
                result = subprocess.run(
                    ['git', 'diff', '--cached'],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    check=True
                )
            else:
                # Get unstaged changes
                result = subprocess.run(
                    ['git', 'diff'],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    check=True
                )
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Error getting git diff: {e}"
        except FileNotFoundError:
            return "Git not found. Make sure you're in a git repository."
    
    def get_changed_files(self):
        """Get list of changed files."""
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                check=True
            )
            return result.stdout.strip().split('\n') if result.stdout else []
        except:
            return []
    
    def analyze_changes(self, diff_text):
        """Analyze the diff to extract key information."""
        lines = diff_text.split('\n')
        
        analysis = {
            'files_changed': [],
            'additions': 0,
            'deletions': 0,
            'key_changes': []
        }
        
        for line in lines:
            if line.startswith('+++'):
                file_name = line.replace('+++ b/', '').strip()
                if file_name and file_name != '/dev/null':
                    analysis['files_changed'].append(file_name)
            elif line.startswith('+') and not line.startswith('+++'):
                analysis['additions'] += 1
                # Extract important additions (function names, class names, etc.)
                if 'def ' in line or 'class ' in line or 'function ' in line:
                    analysis['key_changes'].append(line.strip())
            elif line.startswith('-') and not line.startswith('---'):
                analysis['deletions'] += 1
        
        return analysis
    
    def get_similar_commits(self, diff_summary, top_k=3):
        """Retrieve similar commits from the dataset."""
        results = self.rag.retrieve(diff_summary, top_k=top_k)
        return results
    
    def generate_commit_message(self, diff_text=None, custom_context=""):
        """Generate a commit message using Groq LLM with RAG context."""
        
        # Get diff if not provided
        if diff_text is None:
            diff_text = self.get_git_diff(staged=True)
            if not diff_text or diff_text.startswith("Error") or diff_text.startswith("Git not found"):
                return {"error": diff_text or "No staged changes found"}
        
        # Analyze changes
        analysis = self.analyze_changes(diff_text)
        changed_files = ', '.join(analysis['files_changed'][:5])
        
        # Create summary for RAG retrieval
        diff_summary = f"{changed_files} {' '.join(analysis['key_changes'][:3])}"
        
        # Get similar commits from RAG
        similar_commits = self.get_similar_commits(diff_summary, top_k=3)
        
        # Build context from similar commits
        rag_context = "\n".join([
            f"- {commit['message']}" 
            for commit in similar_commits
        ])
        
        # Truncate diff if too long
        diff_preview = diff_text[:2000] + "..." if len(diff_text) > 2000 else diff_text
        
        # Create prompt for Groq
        prompt = f"""You are an expert at writing clear, concise git commit messages following conventional commit standards.

Based on the following git diff and similar commit examples, generate a professional commit message.

FILES CHANGED: {changed_files}
ADDITIONS: {analysis['additions']} lines
DELETIONS: {analysis['deletions']} lines

SIMILAR COMMIT MESSAGES FROM THIS PROJECT:
{rag_context}

GIT DIFF:
{diff_preview}

{custom_context}

Generate a commit message that:
1. Starts with a type (feat/fix/docs/style/refactor/test/chore)
2. Has a clear, concise subject line (50 chars max)
3. Optionally includes a body explaining the changes
4. Follows the style of similar commits from this project

Return ONLY the commit message, nothing else."""

        try:
            # Call Groq API
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a git commit message expert. Generate clear, professional commit messages."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=500
            )
            
            commit_message = chat_completion.choices[0].message.content.strip()
            
            return {
                "commit_message": commit_message,
                "analysis": analysis,
                "similar_commits": similar_commits
            }
            
        except Exception as e:
            return {"error": f"Error calling Groq API: {str(e)}"}


def main():
    """Main function for CLI usage."""
    print("="*80)
    print("AI Commit Message Generator (RAG + Groq)")
    print("="*80)
    
    # Check for API key
    if not os.getenv('GROQ_API_KEY'):
        print("\nError: GROQ_API_KEY environment variable not set.")
        print("Get your API key from: https://console.groq.com/")
        print("\nSet it with: export GROQ_API_KEY='your-api-key'")
        return
    
    try:
        generator = CommitMessageGenerator()
        
        # Auto-stage all changes
        print("\nAuto-staging all changes (git add .)...")
        try:
            subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
            print("✅ Changes staged successfully")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Warning: Could not stage changes: {e}")
        
        print("\nAnalyzing staged changes...")
        result = generator.generate_commit_message()
        
        if "error" in result:
            print(f"\n❌ {result['error']}")
            return
        
        print("\n" + "="*80)
        print("GENERATED COMMIT MESSAGE:")
        print("="*80)
        print(result['commit_message'])
        
        print("\n" + "="*80)
        print("ANALYSIS:")
        print("="*80)
        print(f"Files changed: {len(result['analysis']['files_changed'])}")
        print(f"Lines added: {result['analysis']['additions']}")
        print(f"Lines deleted: {result['analysis']['deletions']}")
        
        print("\n" + "="*80)
        print("SIMILAR COMMITS (for context):")
        print("="*80)
        for i, commit in enumerate(result['similar_commits'], 1):
            print(f"{i}. {commit['message'][:80]}...")
        
        # Ask if user wants to commit
        print("\n" + "="*80)
        choice = input("\nUse this commit message? (y/n): ").strip().lower()
        
        if choice == 'y':
            try:
                subprocess.run(
                    ['git', 'commit', '-m', result['commit_message']],
                    check=True
                )
                print("✅ Committed successfully!")
            except subprocess.CalledProcessError:
                print("❌ Failed to commit. You can copy the message manually.")
        else:
            print("Commit message not used. You can copy it manually if needed.")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
