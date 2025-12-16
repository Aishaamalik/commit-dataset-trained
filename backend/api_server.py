"""
Flask API server for the AI Commit Message Generator
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import subprocess
import shutil
from commit_generator import CommitMessageGenerator
from github_api import GitHubAPI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='../frontend/build')
CORS(app)

# Global state
current_repo_path = None
generator = None
github_clients = {}  # Store GitHub API clients per user token

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
            # Only skip .git directory (keep all other files including hidden ones)
            if item == '.git':
                continue
            
            # Skip these only if we're in the root project directory (not in cloned repos)
            if current_path == '' and base_path == '.':
                if item in ['__pycache__', 'node_modules', 'build', 'rag_model.pkl', 'cloned_repos', 'frontend', '.env', 'venv', '.venv']:
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
            # Skip node_modules and __pycache__ subdirectories for performance
            if is_dir:
                if item not in ['node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build']:
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
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass


def force_remove_directory(path):
    """Forcefully remove a directory, handling Windows file locks."""
    import time
    import stat
    
    if not os.path.exists(path):
        return True
    
    # Try multiple times with different methods
    for attempt in range(3):
        try:
            # Method 1: Use shutil with error handler
            shutil.rmtree(path, onerror=remove_readonly)
            return True
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            
            # Method 2: Try to make everything writable first
            try:
                for root, dirs, files in os.walk(path):
                    for d in dirs:
                        try:
                            os.chmod(os.path.join(root, d), stat.S_IWRITE)
                        except:
                            pass
                    for f in files:
                        try:
                            os.chmod(os.path.join(root, f), stat.S_IWRITE)
                        except:
                            pass
            except:
                pass
            
            # Wait a bit before retry
            time.sleep(0.5)
    
    # If all else fails, try git clean
    try:
        subprocess.run(['git', 'clean', '-fdx'], cwd=path, capture_output=True)
        shutil.rmtree(path, onerror=remove_readonly)
        return True
    except:
        pass
    
    return False


@app.route('/api/repo/clone', methods=['POST'])
def clone_repo():
    """Clone a repository."""
    global current_repo_path
    try:
        data = request.json
        repo_url = data.get('url')
        
        if not repo_url:
            return jsonify({'error': 'Repository URL is required'}), 400
        
        # Check if git is available
        try:
            git_check = subprocess.run(
                ['git', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if git_check.returncode != 0:
                return jsonify({'error': 'Git is not installed or not accessible'}), 400
        except FileNotFoundError:
            return jsonify({'error': 'Git is not installed. Please install Git and add it to your PATH'}), 400
        except subprocess.TimeoutExpired:
            return jsonify({'error': 'Git command timed out. Please check your Git installation'}), 400
        
        # Extract repo name from URL
        repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
        repo_path = os.path.join('cloned_repos', repo_name)
        
        # Remove if exists (handle Windows readonly files)
        if os.path.exists(repo_path):
            print(f"Removing existing repository at {repo_path}...")
            if not force_remove_directory(repo_path):
                # If we can't remove it, try using a different name
                import time
                repo_name = f"{repo_name}_{int(time.time())}"
                repo_path = os.path.join('cloned_repos', repo_name)
                print(f"Using alternative path: {repo_path}")
        
        # Create directory
        os.makedirs('cloned_repos', exist_ok=True)
        
        # Clone repository with timeout
        print(f"Cloning {repo_url} to {repo_path}...")
        result = subprocess.run(
            ['git', 'clone', repo_url, repo_path],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            error_msg = result.stderr or result.stdout
            
            # Provide more specific error messages
            if 'fatal: repository' in error_msg.lower() and 'not found' in error_msg.lower():
                return jsonify({'error': 'Repository not found. Please check the URL and your access permissions.'}), 400
            elif 'permission denied' in error_msg.lower():
                return jsonify({'error': 'Permission denied. You may need to authenticate with GitHub or check repository access.'}), 400
            elif 'could not resolve host' in error_msg.lower():
                return jsonify({'error': 'Network error. Please check your internet connection.'}), 400
            else:
                return jsonify({'error': f'Failed to clone: {error_msg}'}), 400
        
        current_repo_path = repo_path
        print(f"Successfully cloned to {repo_path}")
        
        return jsonify({
            'success': True,
            'message': f'Repository cloned successfully',
            'path': repo_path,
            'name': repo_name
        })
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Clone operation timed out. The repository might be too large or network is slow.'}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


@app.route('/api/repo/info', methods=['GET'])
def get_repo_info():
    """Get current repository info."""
    global current_repo_path
    return jsonify({
        'path': current_repo_path,
        'active': current_repo_path is not None
    })


@app.route('/api/system/check', methods=['GET'])
def system_check():
    """Check system requirements."""
    checks = {}
    
    # Check Git
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            checks['git'] = {
                'available': True,
                'version': result.stdout.strip()
            }
        else:
            checks['git'] = {
                'available': False,
                'error': 'Git command failed'
            }
    except FileNotFoundError:
        checks['git'] = {
            'available': False,
            'error': 'Git not found in PATH'
        }
    except subprocess.TimeoutExpired:
        checks['git'] = {
            'available': False,
            'error': 'Git command timed out'
        }
    
    return jsonify(checks)


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
        
        # Check if file is binary
        binary_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.ico', '.pdf', '.zip', '.tar', '.gz', 
                            '.exe', '.dll', '.so', '.dylib', '.bin', '.dat', '.db', '.sqlite',
                            '.woff', '.woff2', '.ttf', '.eot', '.mp3', '.mp4', '.avi', '.mov']
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext in binary_extensions:
            return jsonify({
                'error': 'Binary file cannot be displayed',
                'binary': True,
                'path': rel_path
            }), 400
        
        # Check file size (limit to 1MB for performance)
        file_size = os.path.getsize(file_path)
        if file_size > 1024 * 1024:  # 1MB
            return jsonify({
                'error': f'File too large ({file_size // 1024} KB). Maximum size is 1MB.',
                'path': rel_path
            }), 400
        
        # Try to read as text with multiple encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        content = None
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        if content is None:
            # Last resort: read as binary and decode with errors='replace'
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
        
        return jsonify({'content': content, 'path': rel_path})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error reading file: {str(e)}'}), 500


@app.route('/api/file/save', methods=['POST'])
def save_file():
    """Save file content."""
    try:
        base_path = get_repo_path()
        data = request.json
        rel_path = data.get('path')
        content = data.get('content')
        
        file_path = os.path.join(base_path, rel_path)
        
        print(f"Saving file: {file_path}")
        print(f"Base path: {base_path}")
        print(f"Relative path: {rel_path}")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"File saved successfully: {file_path}")
        
        # Verify the file was saved
        if os.path.exists(file_path):
            print(f"File exists and size is: {os.path.getsize(file_path)} bytes")
        
        return jsonify({'success': True, 'message': 'File saved'})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/git/status', methods=['GET'])
def git_status():
    """Get git status."""
    try:
        # Only check status if a repo is cloned
        if current_repo_path is None:
            print("No repository loaded")
            return jsonify({'files': []})
        
        repo_path = get_repo_path()
        print(f"Checking git status in: {repo_path}")
        
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=repo_path
        )
        
        print(f"Git status output: {result.stdout}")
        print(f"Git status stderr: {result.stderr}")
        
        files = []
        for line in result.stdout.split('\n'):
            if line.strip():
                status = line[:2]
                filename = line[3:]
                files.append({
                    'file': filename,
                    'status': status.strip()
                })
        
        print(f"Found {len(files)} changed files")
        return jsonify({'files': files})
    except Exception as e:
        import traceback
        traceback.print_exc()
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


# ============================================================================
# GitHub API Endpoints
# ============================================================================

def get_github_client(token: str) -> GitHubAPI:
    """Get or create GitHub API client for a token."""
    if token not in github_clients:
        github_clients[token] = GitHubAPI(token)
    return github_clients[token]


@app.route('/api/github/connect', methods=['POST'])
def github_connect():
    """Store GitHub access token."""
    try:
        data = request.json
        token = data.get('token')
        
        if not token:
            return jsonify({'error': 'Token is required'}), 400
        
        # Verify token by getting user info
        client = get_github_client(token)
        user_info = client.get_user_info()
        
        if not user_info['success']:
            return jsonify({'error': 'Invalid token'}), 401
        
        return jsonify({
            'success': True,
            'user': user_info['data']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/github/user', methods=['GET'])
def github_user():
    """Get GitHub user information."""
    try:
        token = request.headers.get('X-GitHub-Token')
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        client = get_github_client(token)
        result = client.get_user_info()
        
        if not result['success']:
            return jsonify({'error': result['error']}), 400
        
        return jsonify(result['data'])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/github/repos', methods=['GET'])
def github_repos():
    """List user's GitHub repositories."""
    try:
        token = request.headers.get('X-GitHub-Token')
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 30, type=int)
        
        client = get_github_client(token)
        result = client.list_repositories(per_page=per_page, page=page)
        
        if not result['success']:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({'repositories': result['data']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/github/repos/create', methods=['POST'])
def github_create_repo():
    """Create a new GitHub repository."""
    try:
        token = request.headers.get('X-GitHub-Token')
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        data = request.json
        name = data.get('name')
        description = data.get('description', '')
        private = data.get('private', False)
        
        if not name:
            return jsonify({'error': 'Repository name is required'}), 400
        
        client = get_github_client(token)
        result = client.create_repository(name=name, description=description, private=private)
        
        if not result['success']:
            return jsonify({'error': result['error']}), 400
        
        return jsonify(result['data'])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/github/upload', methods=['POST'])
def github_upload_project():
    """Upload a local project to a new GitHub repository."""
    try:
        token = request.headers.get('X-GitHub-Token')
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        data = request.json
        local_path = data.get('local_path')
        repo_name = data.get('repo_name')
        description = data.get('description', '')
        private = data.get('private', False)
        commit_message = data.get('commit_message', 'Initial commit')
        
        if not local_path or not repo_name:
            return jsonify({'error': 'local_path and repo_name are required'}), 400
        
        # Convert to absolute path if relative
        if not os.path.isabs(local_path):
            local_path = os.path.abspath(local_path)
        
        client = get_github_client(token)
        result = client.upload_project(
            local_path=local_path,
            repo_name=repo_name,
            description=description,
            private=private,
            commit_message=commit_message
        )
        
        if not result['success']:
            return jsonify({'error': result['error']}), 400
        
        return jsonify(result['data'])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/github/repos/delete', methods=['DELETE'])
def github_delete_repo():
    """Delete a GitHub repository."""
    try:
        token = request.headers.get('X-GitHub-Token')
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        data = request.json
        owner = data.get('owner')
        repo = data.get('repo')
        
        if not owner or not repo:
            return jsonify({'error': 'owner and repo are required'}), 400
        
        client = get_github_client(token)
        result = client.delete_repository(owner=owner, repo=repo)
        
        if not result['success']:
            return jsonify({'error': result['error']}), 400
        
        return jsonify({'success': True, 'message': result['message']})
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
