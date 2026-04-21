# -*- coding: utf-8 -*-

"""
Setup Codecov.io upload token as a GitHub Actions secret.

This script:
1. Uses Codecov API token to fetch the repository's upload token
2. Sets the upload token as a GitHub Actions secret

Required environment variables:
- GITHUB_TOKEN: GitHub personal access token with repo scope
- CODECOV_TOKEN: Codecov.io API token (NOT the upload token)

The script is idempotent - it will create or update the secret as needed.
"""

# ------------------------------------------------------------------------------
# Environment Variable Names
# ------------------------------------------------------------------------------
ENV_GITHUB_TOKEN = "GITHUB_TOKEN"
ENV_CODECOV_API_TOKEN = "CODECOV_TOKEN"  # API token for calling Codecov API

# ------------------------------------------------------------------------------
# GitHub Secret Name
# ------------------------------------------------------------------------------
GITHUB_SECRET_NAME = "CODECOV_TOKEN"  # The upload token will be stored with this name

import os
import sys

try:
    from github import Github, GithubException, Auth
    import httpx
except ImportError:
    print("Error: PyGithub or httpx not installed. Run: uv sync --extra mise")
    sys.exit(1)

from utils import get_github_repo_info


def get_codecov_upload_token(github_owner: str, repo_name: str, api_token: str) -> str:
    """
    Fetch the upload token for a repository from Codecov API.

    Ref:
    - https://docs.codecov.com/reference/repos_retrieve
    - https://docs.codecov.com/reference/repos_config_retrieve
    """
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_token}",
    }
    endpoint = "https://api.codecov.io/api/v2"

    with httpx.Client(timeout=30) as client:
        # First, check if repo exists and is public
        url = f"{endpoint}/github/{github_owner}/repos/{repo_name}/"
        response = client.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Error: Failed to get repository info from Codecov")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            sys.exit(1)

        is_private = response.json().get("private", False)
        if is_private:
            print("Error: Cannot use codecov.io for private repositories")
            sys.exit(1)

        # Get the upload token
        url = f"{endpoint}/github/{github_owner}/repos/{repo_name}/config/"
        response = client.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Error: Failed to get upload token from Codecov")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            sys.exit(1)

        upload_token = response.json().get("upload_token")
        if not upload_token:
            print("Error: Upload token not found in Codecov response")
            sys.exit(1)

        return upload_token


def main():
    # Get tokens from environment
    github_token = os.environ.get(ENV_GITHUB_TOKEN)
    codecov_api_token = os.environ.get(ENV_CODECOV_API_TOKEN)

    if not github_token:
        print(f"Error: {ENV_GITHUB_TOKEN} environment variable not set")
        print("Create a token at: https://github.com/settings/tokens")
        sys.exit(1)

    if not codecov_api_token:
        print(f"Error: {ENV_CODECOV_API_TOKEN} environment variable not set")
        print("Get your API token at: https://app.codecov.io/account/gh/<username>/access")
        sys.exit(1)

    owner, repo_name = get_github_repo_info()
    repo_fullname = f"{owner}/{repo_name}"

    print(f"Setting up Codecov upload token for: {repo_fullname}")

    # Step 1: Get upload token from Codecov API
    print(f"Fetching upload token from Codecov API...")
    upload_token = get_codecov_upload_token(owner, repo_name, codecov_api_token)
    print(f"✅ Got upload token from Codecov")

    # Step 2: Set it as GitHub secret
    secrets_url = f"https://github.com/{repo_fullname}/settings/secrets/actions"
    print(f"Setting GitHub secret... (preview at: {secrets_url})")

    gh = Github(auth=Auth.Token(github_token))

    try:
        repo = gh.get_repo(repo_fullname)
    except GithubException as e:
        print(f"Error: Could not access repository {repo_fullname}")
        print(f"Details: {e}")
        sys.exit(1)

    # Create or update the secret (idempotent)
    try:
        repo.create_secret(
            secret_name=GITHUB_SECRET_NAME,
            unencrypted_value=upload_token,
            secret_type="actions",
        )
        print(f"✅ Successfully set {GITHUB_SECRET_NAME} secret on {repo_fullname}")
    except GithubException as e:
        print(f"Error: Failed to create/update secret")
        print(f"Details: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
