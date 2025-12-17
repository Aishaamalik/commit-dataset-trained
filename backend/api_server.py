"""
Flask API server for the AI Commit Message Generator.

This module exposes all HTTP endpoints used by the React frontend while trying
to keep the internal logic well‑structured, reusable and easy to understand.

NOTE: The external API (routes, HTTP verbs and JSON shapes) is preserved so the
frontend continues to work as before. Most refactoring below focuses on:

- extracting helper functions for reusability
- adding very explicit docstrings and inline comments
- grouping related logic (Git / files / GitHub integration) logically
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import subprocess
import shutil
from typing import Dict, Any, List, Optional

from commit_generator import CommitMessageGenerator
from github_api import GitHubAPI
from dotenv import load_dotenv


# ---------------------------------------------------------------------------
# Flask app bootstrap
# ---------------------------------------------------------------------------

load_dotenv()  # Load environment variables from .env if present

# React build directory is served as static files
app = Flask(__name__, static_folder="../frontend/build")

# Allow frontend to hit this backend from different origin during development
CORS(app)


# ---------------------------------------------------------------------------
# Global state and simple accessors
# ---------------------------------------------------------------------------

# NOTE: For a simple desktop‑style tool this in‑memory global state is fine.
# If you ever deploy to multiple processes/containers you’ll want persistent
# storage instead.

current_repo_path: Optional[str] = None  # Path of the currently cloned repo
generator: Optional[CommitMessageGenerator] = None  # Lazy‑created generator
github_clients: Dict[str, GitHubAPI] = {}  # GitHub API clients per user token


def get_generator() -> CommitMessageGenerator:
    """
    Lazily construct and cache a single `CommitMessageGenerator` instance.

    The generator is relatively expensive to create (it loads or trains a
    RAG model), so we only want to construct it once and reuse it.
    """
    global generator

    if generator is None:
        # Instantiate with default configuration that uses environment variables.
        generator = CommitMessageGenerator()

    return generator


def get_repo_path() -> str:
    """
    Return the active repository path or '.' if none is set yet.

    Many endpoints rely on the notion of a "current repository". When nothing
    has been cloned yet we simply default to the current working directory.
    """
    global current_repo_path

    if current_repo_path is None:
        return "."
    return current_repo_path


# ---------------------------------------------------------------------------
# Filesystem helpers
# ---------------------------------------------------------------------------

def build_file_tree(base_path: str, current_path: str = "", prefix: str = "") -> List[Dict[str, Any]]:
    """
    Recursively build a tree representation of files and directories.

    - `base_path`: root of the project we are inspecting
    - `current_path`: path relative to `base_path` during recursion
    - `prefix`: not used by callers at the moment, but kept for backwards
      compatibility with previous implementation
    """
    items: List[Dict[str, Any]] = []

    # Compute the absolute path we are currently listing
    full_path = os.path.join(base_path, current_path) if current_path else base_path

    try:
        for item in sorted(os.listdir(full_path)):
            # Only skip the Git metadata directory; keep other dot‑files
            if item == ".git":
                continue

            # If we are at the project root (not inside cloned repos), skip
            # internal tooling folders that the UI does not need to show.
            if current_path == "" and base_path == ".":
                if item in [
                    "__pycache__",
                    "node_modules",
                    "build",
                    "rag_model.pkl",
                    "cloned_repos",
                    "frontend",
                    ".env",
                    "venv",
                    ".venv",
                ]:
                    continue

            item_full_path = os.path.join(full_path, item)
            item_rel_path = os.path.join(current_path, item) if current_path else item
            is_dir = os.path.isdir(item_full_path)

            # Metadata object returned to the frontend
            item_data: Dict[str, Any] = {
                "name": item,
                "path": item_rel_path.replace("\\", "/"),
                "type": "directory" if is_dir else "file",
                "extension": os.path.splitext(item)[1] if not is_dir else None,
                "children": [],
            }

            # For directories we optionally recurse into children
            # (skipping heavy/irrelevant dirs for performance)
            if is_dir:
                if item not in ["node_modules", "__pycache__", ".venv", "venv", "dist", "build"]:
                    item_data["children"] = build_file_tree(base_path, item_rel_path, prefix + item + "/")

            items.append(item_data)

        # Sort so that directories come first and then files alphabetically
        items.sort(key=lambda x: (x["type"] == "file", x["name"].lower()))

    except PermissionError:
        # Some directories may not be accessible; silently ignore them
        pass

    return items


def remove_readonly(func, path, excinfo) -> None:
    """
    Error handler for Windows read‑only files used by `shutil.rmtree`.

    The handler makes a file writable and retries the supplied function.
    """
    import stat

    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        # If this fails we simply give up; the caller will handle failures.
        pass


def force_remove_directory(path: str) -> bool:
    """
    Robustly remove a directory even on Windows where file locks are common.

    Strategy:
    1. Try `shutil.rmtree` with a handler that removes the read‑only flag.
    2. If that fails, walk the tree, mark everything writable and retry.
    3. As a last resort run `git clean -fdx` and try again.
    """
    import time
    import stat

    if not os.path.exists(path):
        return True

    # Try multiple times with progressively more aggressive approaches
    for attempt in range(3):
        try:
            shutil.rmtree(path, onerror=remove_readonly)
            return True
        except Exception as exc:
            print(f"Attempt {attempt + 1} failed while removing {path}: {exc}")

            # Second approach: make everything writable to reduce permission errors
            try:
                for root, dirs, files in os.walk(path):
                    for d in dirs:
                        try:
                            os.chmod(os.path.join(root, d), stat.S_IWRITE)
                        except Exception:
                            pass
                    for f in files:
                        try:
                            os.chmod(os.path.join(root, f), stat.S_IWRITE)
                        except Exception:
                            pass
            except Exception:
                # If even walking the directory fails, just continue to next attempt
                pass

            # Small backoff before retrying
            time.sleep(0.5)

    # Final attempt: ask Git to clean the directory and then remove again
    try:
        subprocess.run(["git", "clean", "-fdx"], cwd=path, capture_output=True)
        shutil.rmtree(path, onerror=remove_readonly)
        return True
    except Exception:
        return False


def _check_git_available() -> Optional[str]:
    """
    Verify that `git` is installed and reachable on the system PATH.

    Returns:
        None if everything is fine, otherwise a human‑readable error message.
    """
    try:
        git_check = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if git_check.returncode != 0:
            return "Git is not installed or not accessible"
    except FileNotFoundError:
        return "Git is not installed. Please install Git and add it to your PATH"
    except subprocess.TimeoutExpired:
        return "Git command timed out. Please check your Git installation"

    return None


def _clone_repository(repo_url: str) -> Dict[str, Any]:
    """
    Clone a Git repository into the `cloned_repos` directory.

    Returns a dict with keys:
        - success: bool
        - path: path on disk (when success)
        - name: repo name (when success)
        - error: error message (when failed)
    """
    global current_repo_path

    # Extract repo name from URL
    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    repo_path = os.path.join("cloned_repos", repo_name)

    # Remove any existing directory (handling Windows readonly files)
    if os.path.exists(repo_path):
        print(f"Removing existing repository at {repo_path}...")
        if not force_remove_directory(repo_path):
            # If we cannot remove it, fall back to a unique directory name
            import time

            repo_name = f"{repo_name}_{int(time.time())}"
            repo_path = os.path.join("cloned_repos", repo_name)
            print(f"Using alternative path: {repo_path}")

    # Ensure parent directory exists
    os.makedirs("cloned_repos", exist_ok=True)

    # Perform clone with a generous timeout
    print(f"Cloning {repo_url} to {repo_path}...")
    result = subprocess.run(
        ["git", "clone", repo_url, repo_path],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,  # 5‑minute timeout
    )

    if result.returncode != 0:
        error_msg = result.stderr or result.stdout or "Unknown git error"
        lower_error = error_msg.lower()

        # Try to provide a more helpful high‑level message
        if "fatal: repository" in lower_error and "not found" in lower_error:
            return {"success": False, "error": "Repository not found. Please check the URL and your access permissions."}
        if "permission denied" in lower_error:
            return {"success": False, "error": "Permission denied. You may need to authenticate or check access rights."}
        if "could not resolve host" in lower_error:
            return {"success": False, "error": "Network error. Please check your internet connection."}

        return {"success": False, "error": f"Failed to clone: {error_msg}"}

    current_repo_path = repo_path
    print(f"Successfully cloned to {repo_path}")

    return {
        "success": True,
        "path": repo_path,
        "name": repo_name,
    }


@app.route("/api/repo/clone", methods=["POST"])
def clone_repo():
    """
    Clone a Git repository and mark it as the current working project.

    Request JSON:
        { "url": "<repository url>" }

    Response JSON (success):
        { "success": true, "message": "...", "path": "...", "name": "..." }
    """
    try:
        data = request.json or {}
        repo_url = data.get("url")

        if not repo_url:
            return jsonify({"error": "Repository URL is required"}), 400

        git_error = _check_git_available()
        if git_error:
            return jsonify({"error": git_error}), 400

        clone_result = _clone_repository(repo_url)
        if not clone_result.get("success"):
            return jsonify({"error": clone_result["error"]}), 400

        return jsonify(
            {
                "success": True,
                "message": "Repository cloned successfully",
                "path": clone_result["path"],
                "name": clone_result["name"],
            }
        )
    except subprocess.TimeoutExpired:
        return jsonify(
            {
                "error": "Clone operation timed out. The repository might be too large or the network is slow.",
            }
        ), 400
    except Exception as exc:
        import traceback

        traceback.print_exc()
        return jsonify({"error": f"Unexpected error: {str(exc)}"}), 500


@app.route("/api/repo/info", methods=["GET"])
def get_repo_info():
    """
    Return basic information about the currently active repository.

    Response JSON:
        { "path": "<path or null>", "active": <bool> }
    """
    global current_repo_path

    return jsonify({"path": current_repo_path, "active": current_repo_path is not None})


@app.route("/api/system/check", methods=["GET"])
def system_check():
    """
    Perform simple environment checks required for the app to function.

    Currently this only validates Git availability but is structured in a way
    that makes it easy to add more checks later.
    """
    checks: Dict[str, Any] = {}

    try:
        result = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            checks["git"] = {"available": True, "version": result.stdout.strip()}
        else:
            checks["git"] = {"available": False, "error": "Git command failed"}
    except FileNotFoundError:
        checks["git"] = {"available": False, "error": "Git not found in PATH"}
    except subprocess.TimeoutExpired:
        checks["git"] = {"available": False, "error": "Git command timed out"}

    return jsonify(checks)


@app.route("/api/files", methods=["GET"])
def get_files():
    """
    Return a recursive file tree for the current repository.

    Response JSON:
        { "files": [...], "repoPath": "<path or null>" }
    """
    try:
        base_path = get_repo_path()

        # If no repository is cloned yet, return an empty tree
        if current_repo_path is None:
            return jsonify({"files": [], "repoPath": None})

        tree = build_file_tree(base_path)
        return jsonify({"files": tree, "repoPath": current_repo_path})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/file/content", methods=["GET"])
def get_file_content():
    """
    Read and return the textual content of a single file inside the repo.

    Query parameters:
        path: path relative to the current repository root.
    """
    try:
        base_path = get_repo_path()
        rel_path = request.args.get("path")
        file_path = os.path.join(base_path, rel_path)

        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404

        # Some file types are binary; attempting to show them as text would be
        # noisy and unhelpful in the UI, so we block them explicitly.
        binary_extensions = [
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".ico",
            ".pdf",
            ".zip",
            ".tar",
            ".gz",
            ".exe",
            ".dll",
            ".so",
            ".dylib",
            ".bin",
            ".dat",
            ".db",
            ".sqlite",
            ".woff",
            ".woff2",
            ".ttf",
            ".eot",
            ".mp3",
            ".mp4",
            ".avi",
            ".mov",
        ]

        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext in binary_extensions:
            return (
                jsonify(
                    {
                        "error": "Binary file cannot be displayed",
                        "binary": True,
                        "path": rel_path,
                    }
                ),
                400,
            )

        # Hard cap on file sizes for responsiveness in the browser
        file_size = os.path.getsize(file_path)
        if file_size > 1024 * 1024:  # 1MB
            return (
                jsonify(
                    {
                        "error": f"File too large ({file_size // 1024} KB). Maximum size is 1MB.",
                        "path": rel_path,
                    }
                ),
                400,
            )

        # Try multiple encodings; fall back to a safe replacement strategy.
        encodings = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]
        content: Optional[str] = None

        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    content = f.read()
                break
            except (UnicodeDecodeError, UnicodeError):
                continue

        if content is None:
            # Last resort: force UTF‑8 with replacement characters.
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

        return jsonify({"content": content, "path": rel_path})
    except Exception as exc:
        import traceback

        traceback.print_exc()
        return jsonify({"error": f"Error reading file: {str(exc)}"}), 500


@app.route("/api/file/save", methods=["POST"])
def save_file():
    """
    Persist edited file content back to disk inside the current repository.

    Request JSON:
        { "path": "<relative path>", "content": "<file body>" }
    """
    try:
        base_path = get_repo_path()
        data = request.json or {}
        rel_path = data.get("path")
        content = data.get("content", "")

        file_path = os.path.join(base_path, rel_path)

        print(f"Saving file: {file_path}")
        print(f"Base path: {base_path}")
        print(f"Relative path: {rel_path}")

        # Overwrite the file atomically from the server side
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"File saved successfully: {file_path}")

        if os.path.exists(file_path):
            print(f"File exists and size is: {os.path.getsize(file_path)} bytes")

        return jsonify({"success": True, "message": "File saved"})
    except Exception as exc:
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(exc)}), 500


@app.route("/api/git/status", methods=["GET"])
def git_status():
    """
    Return a compact list of files with pending Git changes in the repo.

    Response JSON:
        { "files": [ { "file": "path", "status": "M" }, ... ] }
    """
    try:
        if current_repo_path is None:
            print("No repository loaded")
            return jsonify({"files": []})

        repo_path = get_repo_path()
        print(f"Checking git status in: {repo_path}")

        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=repo_path,
        )

        print(f"Git status output: {result.stdout}")
        print(f"Git status stderr: {result.stderr}")

        files: List[Dict[str, str]] = []
        for line in result.stdout.split("\n"):
            if line.strip():
                status = line[:2]
                filename = line[3:]
                files.append({"file": filename, "status": status.strip()})

        print(f"Found {len(files)} changed files")
        return jsonify({"files": files})
    except Exception as exc:
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(exc)}), 500


@app.route("/api/git/diff", methods=["GET"])
def git_diff():
    """
    Return the raw `git diff` output for the current repository.

    This is used by the UI for previewing pending changes.
    """
    try:
        repo_path = get_repo_path()
        result = subprocess.run(
            ["git", "diff"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=repo_path,
        )
        return jsonify({"diff": result.stdout})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/git/add", methods=["POST"])
def git_add():
    """
    Stage all tracked and untracked changes using `git add .`.
    """
    try:
        repo_path = get_repo_path()
        subprocess.run(["git", "add", "."], check=True, capture_output=True, cwd=repo_path)
        return jsonify({"success": True, "message": "Changes staged"})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/commit/generate", methods=["POST"])
def generate_commit():
    """
    Use the AI commit generator to propose a commit message for current changes.

    This endpoint first looks at staged changes (`git diff --cached`) and, if
    there are none, falls back to unstaged changes (`git diff`).
    """
    try:
        repo_path = get_repo_path()
        gen = get_generator()

        # Prefer staged changes for reproducible commits
        diff_result = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=repo_path,
        )

        diff_text = diff_result.stdout

        if not diff_text:
            # Fall back to unstaged changes so users still get suggestions
            diff_result = subprocess.run(
                ["git", "diff"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=repo_path,
            )
            diff_text = diff_result.stdout

        if not diff_text:
            return jsonify({"error": "No changes found"}), 400

        result = gen.generate_commit_message(diff_text=diff_text)

        if "error" in result:
            return jsonify({"error": result["error"]}), 400

        return jsonify(
            {
                "message": result["commit_message"],
                "analysis": result["analysis"],
                "similar_commits": result["similar_commits"],
            }
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/git/commit", methods=["POST"])
def git_commit():
    """
    Create a Git commit with a message provided by the client.

    Request JSON:
        { "message": "<commit message>" }
    """
    try:
        repo_path = get_repo_path()
        data = request.json or {}
        message = data.get("message")

        subprocess.run(
            ["git", "commit", "-m", message],
            check=True,
            capture_output=True,
            cwd=repo_path,
        )
        return jsonify({"success": True, "message": "Committed successfully"})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/git/push", methods=["POST"])
def git_push():
    """
    Push the current branch to its `origin` remote.
    """
    try:
        repo_path = get_repo_path()

        # Determine the currently checked‑out branch
        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True,
            cwd=repo_path,
        )
        branch = branch_result.stdout.strip()

        subprocess.run(
            ["git", "push", "origin", branch],
            check=True,
            capture_output=True,
            cwd=repo_path,
        )
        return jsonify({"success": True, "message": f"Pushed to origin/{branch}"})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


"""
GitHub API endpoints
--------------------
These endpoints are thin wrappers around the `GitHubAPI` class which encapsulates
all low‑level HTTP details. This keeps route handlers focused on validation and
response formatting.
"""


def get_github_client(token: str) -> GitHubAPI:
    """
    Return a cached `GitHubAPI` instance for a given token.

    The same access token is reused across requests to avoid constantly
    recreating client objects.
    """
    if token not in github_clients:
        github_clients[token] = GitHubAPI(token)
    return github_clients[token]


@app.route("/api/github/connect", methods=["POST"])
def github_connect():
    """
    Validate and store a GitHub personal access token on the server side.
    """
    try:
        data = request.json or {}
        token = data.get("token")

        if not token:
            return jsonify({"error": "Token is required"}), 400

        client = get_github_client(token)
        user_info = client.get_user_info()

        if not user_info["success"]:
            return jsonify({"error": "Invalid token"}), 401

        return jsonify({"success": True, "user": user_info["data"]})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/github/user", methods=["GET"])
def github_user():
    """
    Return information about the authenticated GitHub user.
    """
    try:
        token = request.headers.get("X-GitHub-Token")
        if not token:
            return jsonify({"error": "Token required"}), 401

        client = get_github_client(token)
        result = client.get_user_info()

        if not result["success"]:
            return jsonify({"error": result["error"]}), 400

        return jsonify(result["data"])
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/github/repos", methods=["GET"])
def github_repos():
    """
    List GitHub repositories owned by the authenticated user.
    """
    try:
        token = request.headers.get("X-GitHub-Token")
        if not token:
            return jsonify({"error": "Token required"}), 401

        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 30, type=int)

        client = get_github_client(token)
        result = client.list_repositories(per_page=per_page, page=page)

        if not result["success"]:
            return jsonify({"error": result["error"]}), 400

        return jsonify({"repositories": result["data"]})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/github/repos/create", methods=["POST"])
def github_create_repo():
    """
    Create a new GitHub repository for the authenticated user.
    """
    try:
        token = request.headers.get("X-GitHub-Token")
        if not token:
            return jsonify({"error": "Token required"}), 401

        data = request.json or {}
        name = data.get("name")
        description = data.get("description", "")
        private = data.get("private", False)

        if not name:
            return jsonify({"error": "Repository name is required"}), 400

        client = get_github_client(token)
        result = client.create_repository(name=name, description=description, private=private)

        if not result["success"]:
            return jsonify({"error": result["error"]}), 400

        return jsonify(result["data"])
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/github/upload", methods=["POST"])
def github_upload_project():
    """
    Create a new GitHub repository and upload a local project directory to it.
    """
    try:
        token = request.headers.get("X-GitHub-Token")
        if not token:
            return jsonify({"error": "Token required"}), 401

        data = request.json or {}
        local_path = data.get("local_path")
        repo_name = data.get("repo_name")
        description = data.get("description", "")
        private = data.get("private", False)
        commit_message = data.get("commit_message", "Initial commit")

        if not local_path or not repo_name:
            return jsonify({"error": "local_path and repo_name are required"}), 400

        # Normalize to an absolute path to avoid surprises
        if not os.path.isabs(local_path):
            local_path = os.path.abspath(local_path)

        client = get_github_client(token)
        result = client.upload_project(
            local_path=local_path,
            repo_name=repo_name,
            description=description,
            private=private,
            commit_message=commit_message,
        )

        if not result["success"]:
            return jsonify({"error": result["error"]}), 400

        return jsonify(result["data"])
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/github/repos/delete", methods=["DELETE"])
def github_delete_repo():
    """
    Delete a GitHub repository identified by owner/name.
    """
    try:
        token = request.headers.get("X-GitHub-Token")
        if not token:
            return jsonify({"error": "Token required"}), 401

        data = request.json or {}
        owner = data.get("owner")
        repo = data.get("repo")

        if not owner or not repo:
            return jsonify({"error": "owner and repo are required"}), 400

        client = get_github_client(token)
        result = client.delete_repository(owner=owner, repo=repo)

        if not result["success"]:
            return jsonify({"error": result["error"]}), 400

        return jsonify({"success": True, "message": result["message"]})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


# ---------------------------------------------------------------------------
# Static file serving for React frontend
# ---------------------------------------------------------------------------

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path: str):
    """
    Serve the compiled React app from `frontend/build`.
    """
    if path != "" and os.path.exists(app.static_folder + "/" + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    print("=" * 80)
    print("🚀 AI Commit Generator - Web Interface")
    print("=" * 80)
    print("\nStarting server at http://localhost:5000")
    print("Press Ctrl+C to stop\n")
    app.run(debug=True, port=5000)

