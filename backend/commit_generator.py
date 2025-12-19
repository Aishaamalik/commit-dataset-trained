"""
AI Commit Message Generator using RAG + Groq LLM.

This module encapsulates the logic that:
1. Reads diffs from the current Git repository.
2. Analyses those diffs for high‑level statistics.
3. Retrieves similar commits via a small RAG system.
4. Calls the Groq LLM to generate a high‑quality commit message.
"""

from __future__ import annotations

import os
import subprocess
from typing import Dict, List, Optional

from dotenv import load_dotenv
from groq import Groq
from jinja2 import Environment, FileSystemLoader, select_autoescape

from rag_system import GitHubCommitsRAG

# Load environment variables (GROQ_API_KEY etc.)
load_dotenv()


class CommitMessageGenerator:
    """
    High‑level service that combines Git, a RAG model and an LLM call.

    This class is used from the Flask API, but it can also be consumed from
    other scripts or tests directly.
    """

    def __init__(self, groq_api_key: Optional[str] = None) -> None:
        """
        Initialise the generator and lazily prepare the RAG model.
        """
        self.api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found. Set it as env variable or pass it explicitly.")

        # Groq client for LLM calls
        self.client = Groq(api_key=self.api_key)

        # RAG system backed by a CSV of historical commits
        self.rag = GitHubCommitsRAG("github_commits_api.csv")

        # Load or train the RAG model on first use
        if os.path.exists("rag_model.pkl"):
            print("Loading RAG model...")
            self.rag.load_model()
        else:
            print("Training RAG model...")
            self.rag.train()
            self.rag.save_model()

        # Initialize Jinja2 environment for template rendering
        template_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )

    # ------------------------------------------------------------------ #
    # Git helpers
    # ------------------------------------------------------------------ #

    def get_git_diff(self, staged: bool = True) -> str:
        """
        Return the raw git diff from the current repository.

        Args:
            staged: if True, show staged (`--cached`) changes only,
                    otherwise show unstaged working‑directory changes.
        """
        try:
            if staged:
                cmd = ["git", "diff", "--cached"]
            else:
                cmd = ["git", "diff"]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=True,
            )
            return result.stdout
        except subprocess.CalledProcessError as exc:
            return f"Error getting git diff: {exc}"
        except FileNotFoundError:
            return "Git not found. Make sure you're in a git repository."

    def get_changed_files(self) -> List[str]:
        """
        Return a list of files that have staged changes.
        """
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=True,
            )
            return result.stdout.strip().split("\n") if result.stdout else []
        except Exception:
            # In a failure scenario we simply return an empty list; the message
            # generation will still work using raw diff content.
            return []

    # ------------------------------------------------------------------ #
    # Diff analysis helpers
    # ------------------------------------------------------------------ #

    def analyze_changes(self, diff_text: str) -> Dict:
        """
        Analyse a diff and extract lightweight statistics and highlights.

        Returns a dict with:
            - files_changed: list[str]
            - additions: int
            - deletions: int
            - key_changes: list[str]
        """
        lines = diff_text.split("\n")

        analysis: Dict[str, object] = {
            "files_changed": [],
            "additions": 0,
            "deletions": 0,
            "key_changes": [],
        }

        for line in lines:
            if line.startswith("+++"):
                file_name = line.replace("+++ b/", "").strip()
                if file_name and file_name != "/dev/null":
                    analysis["files_changed"].append(file_name)
            elif line.startswith("+") and not line.startswith("+++"):
                analysis["additions"] = int(analysis["additions"]) + 1
                # Treat new functions / classes as especially important
                if "def " in line or "class " in line or "function " in line:
                    analysis["key_changes"].append(line.strip())
            elif line.startswith("-") and not line.startswith("---"):
                analysis["deletions"] = int(analysis["deletions"]) + 1

        return analysis

    def get_similar_commits(self, diff_summary: str, top_k: int = 3):
        """
        Retrieve the `top_k` most similar commits from the RAG index.
        """
        return self.rag.retrieve(diff_summary, top_k=top_k)

    # ------------------------------------------------------------------ #
    # LLM integration
    # ------------------------------------------------------------------ #

    def _build_prompt(self, diff_text: str, analysis: Dict, similar_commits, custom_context: str = "") -> str:
        """
        Construct the full textual prompt to send to the Groq LLM using Jinja2 templates.
        """
        changed_files = ", ".join(analysis["files_changed"][:5])

        # Truncate diff aggressively to keep context within reasonable bounds
        diff_preview = diff_text[:2000] + "..." if len(diff_text) > 2000 else diff_text

        # Load and render the user prompt template
        template = self.jinja_env.get_template("user_prompt.jinja")
        prompt = template.render(
            changed_files=changed_files,
            additions=analysis["additions"],
            deletions=analysis["deletions"],
            similar_commits=similar_commits,
            diff_preview=diff_preview,
            custom_context=custom_context
        )
        return prompt

    def _get_system_prompt(self) -> str:
        """
        Get the system prompt from Jinja2 template.
        """
        template = self.jinja_env.get_template("system_prompt.jinja")
        return template.render()

    def generate_commit_message(self, diff_text: Optional[str] = None, custom_context: str = "") -> Dict:
        """
        Generate a commit message using Groq LLM with RAG context.

        Args:
            diff_text: Optional raw diff; if omitted we call `get_git_diff`.
            custom_context: Optional extra natural‑language context for the LLM.
        """
        # If no diff was passed in we read the staged diff from Git
        if diff_text is None:
            diff_text = self.get_git_diff(staged=True)
            if not diff_text or diff_text.startswith("Error") or diff_text.startswith("Git not found"):
                return {"error": diff_text or "No staged changes found"}

        # Analyse the changes to construct a small summary
        analysis = self.analyze_changes(diff_text)
        changed_files = ", ".join(analysis["files_changed"][:5])

        # Compose a short summary string which is used for retrieval
        diff_summary = f"{changed_files} {' '.join(analysis['key_changes'][:3])}"

        # Query the RAG index for prior commits that resemble this change
        similar_commits = self.get_similar_commits(diff_summary, top_k=3)

        # Build the final prompt for the model using Jinja2 templates
        prompt = self._build_prompt(diff_text, analysis, similar_commits, custom_context)
        system_prompt = self._get_system_prompt()

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {"role": "user", "content": prompt},
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=500,
            )

            commit_message = chat_completion.choices[0].message.content.strip()

            return {
                "commit_message": commit_message,
                "analysis": analysis,
                "similar_commits": similar_commits,
            }

        except Exception as exc:  # noqa: BLE001
            return {"error": f"Error calling Groq API: {str(exc)}"}


def main() -> None:
    """
    Small CLI entry point for manual commit‑message generation.
    """
    print("=" * 80)
    print("AI Commit Message Generator (RAG + Groq)")
    print("=" * 80)

    if not os.getenv("GROQ_API_KEY"):
        print("\nError: GROQ_API_KEY environment variable not set.")
        print("Get your API key from: https://console.groq.com/")
        print("\nSet it with: export GROQ_API_KEY='your-api-key'")
        return

    try:
        generator = CommitMessageGenerator()

        # Auto‑stage all changes for convenience when used from CLI
        print("\nAuto-staging all changes (git add .)...")
        try:
            subprocess.run(["git", "add", "."], check=True, capture_output=True)
            print("✅ Changes staged successfully")
        except subprocess.CalledProcessError as exc:
            print(f"⚠️  Warning: Could not stage changes: {exc}")

        print("\nAnalyzing staged changes...")
        result = generator.generate_commit_message()

        if "error" in result:
            print(f"\n❌ {result['error']}")
            return

        print("\n" + "=" * 80)
        print("GENERATED COMMIT MESSAGE:")
        print("=" * 80)
        print(result["commit_message"])

        print("\n" + "=" * 80)
        print("ANALYSIS:")
        print("=" * 80)
        print(f"Files changed: {len(result['analysis']['files_changed'])}")
        print(f"Lines added: {result['analysis']['additions']}")
        print(f"Lines deleted: {result['analysis']['deletions']}")

        print("\n" + "=" * 80)
        print("SIMILAR COMMITS (for context):")
        print("=" * 80)
        for i, commit in enumerate(result["similar_commits"], 1):
            print(f"{i}. {commit['message'][:80]}...")

        print("\n" + "=" * 80)
        choice = input("\nUse this commit message? (y/n): ").strip().lower()

        if choice == "y":
            try:
                subprocess.run(
                    ["git", "commit", "-m", result["commit_message"]],
                    check=True,
                )
                print("✅ Committed successfully!")

                push_choice = input("\nPush to remote? (y/n): ").strip().lower()

                if push_choice == "y":
                    print("\nPushing to remote...")
                    try:
                        branch_result = subprocess.run(
                            ["git", "branch", "--show-current"],
                            capture_output=True,
                            text=True,
                            check=True,
                        )
                        branch_name = branch_result.stdout.strip()

                        subprocess.run(
                            ["git", "push", "origin", branch_name],
                            check=True,
                        )
                        print(f"✅ Pushed to origin/{branch_name} successfully!")
                    except subprocess.CalledProcessError as exc:
                        print(f"❌ Failed to push: {exc}")
                        print("You can push manually with: git push origin main")
                else:
                    print("Changes committed locally. Push manually when ready.")

            except subprocess.CalledProcessError:
                print("❌ Failed to commit. You can copy the message manually.")
        else:
            print("Commit message not used. You can copy it manually if needed.")

    except Exception as exc:  # noqa: BLE001
        print(f"\n❌ Error: {str(exc)}")


if __name__ == "__main__":
    main()

