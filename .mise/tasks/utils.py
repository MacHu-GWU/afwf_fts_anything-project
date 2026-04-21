# -*- coding: utf-8 -*-

"""
Shared utilities for mise tasks.

This module provides common functions used across multiple mise task scripts.
"""

import re
import sys
import subprocess
from pathlib import Path
from functools import cached_property

# Use tomllib (3.11+) or tomli (3.10)
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        print("Error: tomli not installed (required for Python 3.10). Run: uv sync --extra mise")
        sys.exit(1)


class ProjectConfig:
    """
    Lazy-loaded project configuration from pyproject.toml and git.

    All properties are cached after first access.
    """

    @cached_property
    def project_root(self) -> Path:
        """Get the project root directory (parent of .mise/tasks/)."""
        return Path(__file__).parent.parent.parent

    @cached_property
    def pyproject_data(self) -> dict:
        """Load and parse pyproject.toml (cached)."""
        pyproject_path = self.project_root / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            return tomllib.load(f)

    @cached_property
    def project_name(self) -> str:
        """Get project name from pyproject.toml."""
        return self.pyproject_data["project"]["name"]

    @cached_property
    def project_description(self) -> str:
        """Get project description from pyproject.toml."""
        return self.pyproject_data["project"]["description"]

    @cached_property
    def git_remote_url(self) -> str:
        """Get git remote origin URL."""
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            print("Error: Failed to get git remote URL")
            sys.exit(1)

    @cached_property
    def github_owner(self) -> str:
        """Get GitHub repository owner from git remote."""
        match = re.match(
            r"(?:https://github\.com/|git@github\.com:)([^/]+)/(.+?)(?:\.git)?$",
            self.git_remote_url,
        )
        if not match:
            print(f"Error: Could not parse GitHub URL: {self.git_remote_url}")
            sys.exit(1)
        return match.group(1)

    @cached_property
    def github_repo_name(self) -> str:
        """Get GitHub repository name from git remote."""
        match = re.match(
            r"(?:https://github\.com/|git@github\.com:)([^/]+)/(.+?)(?:\.git)?$",
            self.git_remote_url,
        )
        if not match:
            print(f"Error: Could not parse GitHub URL: {self.git_remote_url}")
            sys.exit(1)
        return match.group(2)

    @cached_property
    def github_repo_url(self) -> str:
        """Get GitHub repository HTTPS URL."""
        url = self.git_remote_url
        if url.startswith("git@github.com:"):
            url = url.replace("git@github.com:", "https://github.com/")
        if url.endswith(".git"):
            url = url[:-4]
        return url

    @cached_property
    def readthedocs_slug(self) -> str:
        """Get ReadTheDocs slug (project name with _ replaced by -)."""
        return self.project_name.replace("_", "-")

    @cached_property
    def readthedocs_url(self) -> str:
        """Get ReadTheDocs documentation URL."""
        return f"https://{self.readthedocs_slug}.readthedocs.io/"


# Singleton instance for use across scripts
config = ProjectConfig()


# Convenience functions (for backwards compatibility and simpler imports)
def get_project_root() -> Path:
    return config.project_root

def get_github_repo_info() -> tuple[str, str]:
    """Returns (owner, repo_name)."""
    return config.github_owner, config.github_repo_name

def get_github_repo_url() -> str:
    return config.github_repo_url

def get_project_name() -> str:
    return config.project_name

def get_project_description() -> str:
    return config.project_description

def get_readthedocs_slug() -> str:
    return config.readthedocs_slug

def get_readthedocs_url() -> str:
    return config.readthedocs_url
