"""
Flask API server for the AI Commit Message Generator
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import subprocess
import shutil
from commit_generator import CommitMessageGenerator
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='frontend/build')
CORS(app)

# Global state
current_repo_path = None
generator = None

def get_generator():
    global generator
    if generator is None:
        generator = CommitMessageGenerator()
    return generator

def get_repo_path():
    global current_repo_path
    if current_repo_path is None:
        return '.'
    return current_repo_path


def build_file_tree(base_path, current_path='', prefix=''):
    """Recursively build file tree structure with relative paths."""
    items = []
    
    full_path = os.path.join(base_path, current_path) if current_path else base_path
    
    try:
        for item in sorted(os.listdir(full_path)):
            # Skip hidden files except specific ones
            if item.startswith('.') and item not in ['.gitignore']:
                continue
            # Skip unwanted directories
            if item in ['__pycache__', 'node_modules', 'build', 'rag_model.pkl', '.git', 'cloned_repos', 'frontend']:
                continue
                
            item_full_path = os.path.join(full_path, item)
            item_rel_path = os.path.join(current_path, item) if current_path else item
            is_dir = os.path.isdir(item_full_path)
            
            item_data = {
                'name': item,
                'path': item_rel_path.replace('\\', '/'),
                'type': 'directory' if is_dir else 'file',
                'extension': os.path.splitext(item)[1] if not is_dir else None,
                'children': []
            }
            
            # Recursively get children for directories
            if is_dir:
                item_data['children'] = build_file_tree(base_path, item_rel_path, prefix + item + '/')
            
            items.append(item_data)
        
        # Sort: directories first, then files
        items.sort(key=lambda x: (x['type'] == 'file', x['name'].lower()))
        
    except PermissionError:
        pass
    
    return items


def remove_readonly(func, path, excinfo):
    """Error handler for Windows readonly files."""
    import stat
    os.chmod(path, stat.S_IWRITE)
    func(path)


@app.route('/api/repo/clone', methods=['POST'])
def clone_repo():
    """Clone a repository."""
    global current_repo_path
    try:
        data = request.json
        repo_url = data.get('url')
        
        if not repo_url:
            return jsonify({'error': 'Repository URL is required'}), 400
        
        # Extract repo name from URL
        repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
        repo_path = os.path.join('cloned_repos', repo_name)
        
        # Remove if exists (handle Windows readonly files)
        if os.path.exists(repo_path):
            try:
                shutil.rmtree(repo_path, onerror=remove_readonly)
            except Exception as e:
                # If still fails, try to continue anyway
                print(f"Warning: Could not fully remove old repo: {e}")
        
        # Create directory
        os.makedirs('cloned_repos', exist_ok=True)
        
        # Clone repository
        result = subprocess.run(
            ['git', 'clone', repo_url, repo_path],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode != 0:
            return jsonify({'error': f'Failed to clone: {result.stderr}'}), 400
        
        current_repo_path = repo_path
        return jsonify({
            'success': True,
            'message': f'Repository cloned successfully',
            'path': repo_path,
            'name': repo_name
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/repo/info', methods=['GET'])
def get_repo_info():
    """Get current repository info."""
    global current_repo_path
    return jsonify({
        'path': current_repo_path,
        'active': current_repo_path is not None
    })


@app.route('/api/files', methods=['GET'])
def get_files():
    """Get file tree structure."""
    try:
        base_path = get_repo_path()
        
        # If no repo is cloned, return empty
        if current_repo_path is None:
            return jsonify({'files': [], 'repoPath': None})
        
        tree = build_file_tree(base_path)
        return jsonify({'files': tree, 'repoPath': current_repo_path})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/file/content', methods=['GET'])
def get_file_content():
    """Get content of a specific file."""
    try:
        base_path = get_repo_path()
        rel_path = request.args.get('path')
        file_path = os.path.join(base_path, rel_path)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        return jsonify({'content': content, 'path': rel_path})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/file/save', methods=['POST'])
def save_file():
    """Save file content."""
    try:
        base_path = get_repo_path()
        data = request.json
        rel_path = data.get('path')
        content = data.get('content')
        
        file_path = os.path.join(base_path, rel_path)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return jsonify({'success': True, 'message': 'File saved'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/git/status', methods=['GET'])
def git_status():
    """Get git status."""
    try:
        # Only check status if a repo is cloned
        if current_repo_path is None:
            return jsonify({'files': []})
        
        repo_path = get_repo_path()
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=repo_path
        )
        
        files = []
        for line in result.stdout.split('\n'):
            if line.strip():
                status = line[:2]
                filename = line[3:]
                files.append({
                    'file': filename,
                    'status': status.strip()
                })
        
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/git/diff', methods=['GET'])
def git_diff():
    """Get git diff."""
    try:
        repo_path = get_repo_path()
        result = subprocess.run(
            ['git', 'diff'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=repo_path
        )
        return jsonify({'diff': result.stdout})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/git/add', methods=['POST'])
def git_add():
    """Stage all changes."""
    try:
        repo_path = get_repo_path()
        subprocess.run(['git', 'add', '.'], check=True, capture_output=True, cwd=repo_path)
        return jsonify({'success': True, 'message': 'Changes staged'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/commit/generate', methods=['POST'])
def generate_commit():
    """Generate commit message."""
    try:
        repo_path = get_repo_path()
        gen = get_generator()
        
        # Get diff from the cloned repository
        diff_result = subprocess.run(
            ['git', 'diff', '--cached'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=repo_path
        )
        
        diff_text = diff_result.stdout
        
        if not diff_text:
            # Try unstaged changes
            diff_result = subprocess.run(
                ['git', 'diff'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                cwd=repo_path
            )
            diff_text = diff_result.stdout
        
        if not diff_text:
            return jsonify({'error': 'No changes found'}), 400
        
        result = gen.generate_commit_message(diff_text=diff_text)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({
            'message': result['commit_message'],
            'analysis': result['analysis'],
            'similar_commits': result['similar_commits']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/git/commit', methods=['POST'])
def git_commit():
    """Commit with message."""
    try:
        repo_path = get_repo_path()
        data = request.json
        message = data.get('message')
        
        subprocess.run(
            ['git', 'commit', '-m', message],
            check=True,
            capture_output=True,
            cwd=repo_path
        )
        return jsonify({'success': True, 'message': 'Committed successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/git/push', methods=['POST'])
def git_push():
    """Push to remote."""
    try:
        repo_path = get_repo_path()
        
        # Get current branch
        branch_result = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True,
            text=True,
            check=True,
            cwd=repo_path
        )
        branch = branch_result.stdout.strip()
        
        # Push
        subprocess.run(
            ['git', 'push', 'origin', branch],
            check=True,
            capture_output=True,
            cwd=repo_path
        )
        return jsonify({'success': True, 'message': f'Pushed to origin/{branch}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Serve React frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    print("="*80)
    print("🚀 AI Commit Generator - Web Interface")
    print("="*80)
    print("\nStarting server at http://localhost:5000")
    print("Press Ctrl+C to stop\n")
    app.run(debug=True, port=5000)
