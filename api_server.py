"""
Flask API server for the commit message generator
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from commit_generator import CommitMessageGenerator
from dotenv import load_dotenv
import subprocess
import os

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Initialize generator
generator = None

def get_generator():
    """Lazy load the generator."""
    global generator
    if generator is None:
        generator = CommitMessageGenerator()
    return generator


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok", "message": "API is running"})


@app.route('/api/git-status', methods=['GET'])
def git_status():
    """Get current git status."""
    try:
        # Get unstaged changes
        unstaged = subprocess.run(
            ['git', 'diff', '--name-only'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        # Get staged changes
        staged = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        # Get current branch
        branch = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True,
            text=True
        )
        
        return jsonify({
            "success": True,
            "branch": branch.stdout.strip(),
            "unstaged_files": [f for f in unstaged.stdout.strip().split('\n') if f],
            "staged_files": [f for f in staged.stdout.strip().split('\n') if f]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/stage-all', methods=['POST'])
def stage_all():
    """Stage all changes."""
    try:
        subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
        return jsonify({"success": True, "message": "All changes staged"})
    except subprocess.CalledProcessError as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/generate', methods=['POST'])
def generate_commit():
    """Generate commit message."""
    try:
        data = request.json
        custom_diff = data.get('diff', None)
        custom_context = data.get('context', '')
        
        gen = get_generator()
        result = gen.generate_commit_message(
            diff_text=custom_diff,
            custom_context=custom_context
        )
        
        if "error" in result:
            return jsonify({"success": False, "error": result["error"]}), 400
        
        return jsonify({
            "success": True,
            "commit_message": result["commit_message"],
            "analysis": result["analysis"],
            "similar_commits": result["similar_commits"]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/commit', methods=['POST'])
def commit_changes():
    """Commit with the generated message."""
    try:
        data = request.json
        message = data.get('message')
        
        if not message:
            return jsonify({"success": False, "error": "No commit message provided"}), 400
        
        subprocess.run(
            ['git', 'commit', '-m', message],
            check=True,
            capture_output=True
        )
        
        return jsonify({"success": True, "message": "Committed successfully"})
    except subprocess.CalledProcessError as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/push', methods=['POST'])
def push_changes():
    """Push to remote."""
    try:
        # Get current branch
        branch_result = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True,
            text=True,
            check=True
        )
        branch_name = branch_result.stdout.strip()
        
        # Push
        subprocess.run(
            ['git', 'push', 'origin', branch_name],
            check=True,
            capture_output=True
        )
        
        return jsonify({
            "success": True,
            "message": f"Pushed to origin/{branch_name}"
        })
    except subprocess.CalledProcessError as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    # Check for API key
    if not os.getenv('GROQ_API_KEY'):
        print("⚠️  Warning: GROQ_API_KEY not set!")
    
    print("="*80)
    print("🚀 Starting API Server...")
    print("="*80)
    print("API will be available at: http://localhost:5000")
    print("Frontend should connect to this URL")
    print("="*80)
    
    app.run(debug=True, port=5000)
