"""
GitHub API integration for repository management
"""

import requests
import os
import subprocess
import shutil
from typing import Dict, List, Optional


class GitHubAPI:
    """Handle GitHub API operations."""
    
    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if access_token:
            self.headers["Authorization"] = f"token {access_token}"
    
    def set_token(self, access_token: str):
        """Set or update the GitHub access token."""
        self.access_token = access_token
        self.headers["Authorization"] = f"token {access_token}"
    
    def get_user_info(self) -> Dict:
        """Get authenticated user information."""
        try:
            response = requests.get(
                f"{self.base_url}/user",
                headers=self.headers
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def list_repositories(self, per_page: int = 30, page: int = 1) -> Dict:
        """List user's repositories."""
        try:
            response = requests.get(
                f"{self.base_url}/user/repos",
                headers=self.headers,
                params={
                    "per_page": per_page,
                    "page": page,
                    "sort": "updated",
                    "affiliation": "owner"
                }
            )
            response.raise_for_status()
            
            repos = response.json()
            formatted_repos = []
            
            for repo in repos:
                formatted_repos.append({
                    "id": repo["id"],
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "description": repo["description"],
                    "private": repo["private"],
                    "html_url": repo["html_url"],
                    "clone_url": repo["clone_url"],
                    "created_at": repo["created_at"],
                    "updated_at": repo["updated_at"],
                    "language": repo["language"],
                    "stargazers_count": repo["stargazers_count"],
                    "forks_count": repo["forks_count"]
                })
            
            return {"success": True, "data": formatted_repos}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def create_repository(self, name: str, description: str = "", private: bool = False) -> Dict:
        """Create a new GitHub repository."""
        try:
            response = requests.post(
                f"{self.base_url}/user/repos",
                headers=self.headers,
                json={
                    "name": name,
                    "description": description,
                    "private": private,
                    "auto_init": False
                }
            )
            response.raise_for_status()
            
            repo = response.json()
            return {
                "success": True,
                "data": {
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "html_url": repo["html_url"],
                    "clone_url": repo["clone_url"],
                    "ssh_url": repo["ssh_url"]
                }
            }
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def upload_project(self, local_path: str, repo_name: str, description: str = "", 
                      private: bool = False, commit_message: str = "Initial commit") -> Dict:
        """
        Upload a local project to a new GitHub repository.
        
        Steps:
        1. Create new GitHub repository
        2. Initialize git in local directory (if not already)
        3. Add all files
        4. Commit
        5. Add remote
        6. Push to GitHub
        """
        try:
            # Validate local path
            if not os.path.exists(local_path):
                return {"success": False, "error": "Local path does not exist"}
            
            # Create repository on GitHub
            create_result = self.create_repository(name=repo_name, description=description, private=private)
            if not create_result["success"]:
                return create_result
            
            repo_data = create_result["data"]
            clone_url = repo_data["clone_url"]
            
            # Initialize git if needed
            git_dir = os.path.join(local_path, ".git")
            if not os.path.exists(git_dir):
                subprocess.run(["git", "init"], cwd=local_path, check=True, capture_output=True)
            
            # Add all files
            subprocess.run(["git", "add", "."], cwd=local_path, check=True, capture_output=True)
            
            # Commit
            subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=local_path,
                check=True,
                capture_output=True
            )
            
            # Add remote (remove if exists)
            subprocess.run(
                ["git", "remote", "remove", "origin"],
                cwd=local_path,
                capture_output=True
            )
            subprocess.run(
                ["git", "remote", "add", "origin", clone_url],
                cwd=local_path,
                check=True,
                capture_output=True
            )
            
            # Get current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=local_path,
                capture_output=True,
                text=True,
                check=True
            )
            branch = branch_result.stdout.strip() or "main"
            
            # Rename to main if needed
            if branch != "main":
                subprocess.run(
                    ["git", "branch", "-M", "main"],
                    cwd=local_path,
                    capture_output=True
                )
            
            # Push to GitHub
            subprocess.run(
                ["git", "push", "-u", "origin", "main"],
                cwd=local_path,
                check=True,
                capture_output=True
            )
            
            return {
                "success": True,
                "data": {
                    "message": "Project uploaded successfully",
                    "repository": repo_data
                }
            }
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": f"Git operation failed: {e.stderr.decode() if e.stderr else str(e)}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_repository(self, owner: str, repo: str) -> Dict:
        """Delete a repository."""
        try:
            response = requests.delete(
                f"{self.base_url}/repos/{owner}/{repo}",
                headers=self.headers
            )
            response.raise_for_status()
            return {"success": True, "message": "Repository deleted successfully"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
