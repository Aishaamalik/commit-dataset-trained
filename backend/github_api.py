"""
GitHub API integration for repository management.

This module concentrates all direct communication with the GitHub REST API and
Git CLI for repository creation and upload flows. The higher‑level Flask routes
use this class so they stay small and easy to reason about.
"""

from __future__ import annotations

import os
import subprocess
from typing import Dict, Optional

import requests


class GitHubAPI:
    """
    Thin wrapper around GitHub's REST API plus a few local git operations.

    The methods in this class deliberately return plain dictionaries with
    `"success"`, `"data"` and `"error"` keys to make them easy to consume from
    the Flask layer or other Python code.
    """

    def __init__(self, access_token: Optional[str] = None) -> None:
        """
        Create a new client with an optional personal access token.

        If a token is provided it is added as an Authorization header so GitHub
        can associate all subsequent requests with that user.
        """
        self.access_token = access_token
        self.base_url = "https://api.github.com"
        self.headers = {"Accept": "application/vnd.github.v3+json"}

        if access_token:
            self.headers["Authorization"] = f"token {access_token}"

    # ------------------------------------------------------------------ #
    # Configuration helpers
    # ------------------------------------------------------------------ #

    def set_token(self, access_token: str) -> None:
        """
        Update the GitHub access token after the instance was created.

        Useful when you create the object without a token and set it only after
        the user has gone through an authentication / token entry flow.
        """
        self.access_token = access_token
        self.headers["Authorization"] = f"token {access_token}"

    # ------------------------------------------------------------------ #
    # Simple user / repo metadata operations
    # ------------------------------------------------------------------ #

    def get_user_info(self) -> Dict:
        """
        Fetch information about the currently authenticated GitHub user.
        """
        try:
            response = requests.get(f"{self.base_url}/user", headers=self.headers)
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except requests.exceptions.RequestException as exc:
            return {"success": False, "error": str(exc)}

    def list_repositories(self, per_page: int = 30, page: int = 1) -> Dict:
        """
        List repositories owned by the authenticated user.

        Returns a simplified list of repositories with only the fields that are
        relevant for the UI instead of GitHub's full, verbose payload.
        """
        try:
            response = requests.get(
                f"{self.base_url}/user/repos",
                headers=self.headers,
                params={
                    "per_page": per_page,
                    "page": page,
                    "sort": "updated",
                    "affiliation": "owner",
                },
            )
            response.raise_for_status()

            repos = response.json()
            formatted_repos = []

            for repo in repos:
                formatted_repos.append(
                    {
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
                        "forks_count": repo["forks_count"],
                    }
                )

            return {"success": True, "data": formatted_repos}
        except requests.exceptions.RequestException as exc:
            return {"success": False, "error": str(exc)}

    def create_repository(self, name: str, description: str = "", private: bool = False) -> Dict:
        """
        Create a new GitHub repository owned by the authenticated user.
        """
        try:
            response = requests.post(
                f"{self.base_url}/user/repos",
                headers=self.headers,
                json={"name": name, "description": description, "private": private, "auto_init": False},
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
                    "ssh_url": repo["ssh_url"],
                },
            }
        except requests.exceptions.RequestException as exc:
            return {"success": False, "error": str(exc)}

    # ------------------------------------------------------------------ #
    # Project upload helpers (Git + GitHub)
    # ------------------------------------------------------------------ #

    def upload_project(
        self,
        local_path: str,
        repo_name: str,
        description: str = "",
        private: bool = False,
        commit_message: str = "Initial commit",
    ) -> Dict:
        """
        Upload a local project directory to a brand‑new GitHub repository.

        High‑level steps:
        1. Create the repository on GitHub.
        2. Initialise git locally if needed.
        3. Stage and commit all files.
        4. Configure the `origin` remote.
        5. Push to GitHub.
        """
        try:
            if not os.path.exists(local_path):
                return {"success": False, "error": "Local path does not exist"}

            # 1. Create the repository on GitHub
            create_result = self.create_repository(name=repo_name, description=description, private=private)
            if not create_result["success"]:
                return create_result

            repo_data = create_result["data"]
            clone_url = repo_data["clone_url"]

            # 2. Initialise git if there is no .git directory yet
            git_dir = os.path.join(local_path, ".git")
            if not os.path.exists(git_dir):
                subprocess.run(["git", "init"], cwd=local_path, check=True, capture_output=True)

            # 3. Stage and commit everything
            subprocess.run(["git", "add", "."], cwd=local_path, check=True, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=local_path,
                check=True,
                capture_output=True,
            )

            # 4. Configure the origin remote (remove any existing one first)
            subprocess.run(
                ["git", "remote", "remove", "origin"],
                cwd=local_path,
                capture_output=True,
            )
            subprocess.run(
                ["git", "remote", "add", "origin", clone_url],
                cwd=local_path,
                check=True,
                capture_output=True,
            )

            # 5. Work out the current branch and ensure we push `main`
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=local_path,
                capture_output=True,
                text=True,
                check=True,
            )
            branch = branch_result.stdout.strip() or "main"

            if branch != "main":
                subprocess.run(
                    ["git", "branch", "-M", "main"],
                    cwd=local_path,
                    capture_output=True,
                )

            subprocess.run(
                ["git", "push", "-u", "origin", "main"],
                cwd=local_path,
                check=True,
                capture_output=True,
            )

            return {
                "success": True,
                "data": {
                    "message": "Project uploaded successfully",
                    "repository": repo_data,
                },
            }
        except subprocess.CalledProcessError as exc:
            # stderr may already be bytes or str; handle both safely
            stderr_text = exc.stderr.decode() if hasattr(exc.stderr, "decode") else (exc.stderr or str(exc))
            return {"success": False, "error": f"Git operation failed: {stderr_text}"}
        except Exception as exc:  # noqa: BLE001
            return {"success": False, "error": str(exc)}

    def delete_repository(self, owner: str, repo: str) -> Dict:
        """
        Permanently delete a repository identified by `owner` and `name`.
        """
        try:
            response = requests.delete(f"{self.base_url}/repos/{owner}/{repo}", headers=self.headers)
            response.raise_for_status()
            return {"success": True, "message": "Repository deleted successfully"}
        except requests.exceptions.RequestException as exc:
            return {"success": False, "error": str(exc)}

