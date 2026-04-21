
"""
Update GitHub repository metadata (description and homepage URL).

Required environment variables:
- GITHUB_TOKEN: GitHub personal access token with repo scope

The script reads project info from pyproject.toml and sets:
- description: from pyproject.toml [project].description
- homepage: ReadTheDocs documentation URL
"""

# ------------------------------------------------------------------------------
# Environment Variable Names
# ------------------------------------------------------------------------------
ENV_GITHUB_TOKEN = "GITHUB_TOKEN"

import os
import sys

try:
    from github import Github, GithubException, Auth
except ImportError:
    print("Error: PyGithub not installed. Run: uv sync --extra mise")
    sys.exit(1)

from utils import (
    get_github_repo_info,
    get_project_description,
    get_readthedocs_url,
)


def main():
    # Get token from environment
    github_token = os.environ.get(ENV_GITHUB_TOKEN)

    if not github_token:
        print(f"Error: {ENV_GITHUB_TOKEN} environment variable not set")
        print("Create a token at: https://github.com/settings/tokens")
        sys.exit(1)

    owner, repo_name = get_github_repo_info()
    repo_fullname = f"{owner}/{repo_name}"
    description = get_project_description()
    homepage = get_readthedocs_url()

    print(f"Updating GitHub repository metadata: {repo_fullname}")
    repo_url = f"https://github.com/{repo_fullname}"
    print(f"Preview at: {repo_url}")

    gh = Github(auth=Auth.Token(github_token))

    try:
        repo = gh.get_repo(repo_fullname)
    except GithubException as e:
        print(f"Error: Could not access repository {repo_fullname}")
        print(f"Details: {e}")
        sys.exit(1)

    # Update repository metadata
    try:
        repo.edit(
            description=description,
            homepage=homepage,
        )
        print(f"✅ Successfully updated repository metadata")
        print(f"   Description: {description}")
        print(f"   Homepage: {homepage}")
    except GithubException as e:
        print(f"Error: Failed to update repository metadata")
        print(f"Details: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
