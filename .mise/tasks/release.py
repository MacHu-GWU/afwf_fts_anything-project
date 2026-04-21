# -*- coding: utf-8 -*-

"""
Create a GitHub Release using the current version based on default branch.

Required environment variables:
- GITHUB_TOKEN: GitHub personal access token with repo scope

The script is idempotent:
- Skips if release already exists
- Creates tag if not exists (based on default branch latest commit)
- Creates release with the tag
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
    config,
)


def get_package_version() -> str:
    """Get package version from pyproject.toml."""
    return config.pyproject_data["project"]["version"]


def main():
    # Get token from environment
    github_token = os.environ.get(ENV_GITHUB_TOKEN)

    if not github_token:
        print(f"Error: {ENV_GITHUB_TOKEN} environment variable not set")
        print("Create a token at: https://github.com/settings/tokens")
        sys.exit(1)

    owner, repo_name = get_github_repo_info()
    repo_fullname = f"{owner}/{repo_name}"
    version = get_package_version()
    release_name = version  # e.g., "1.0.0"

    print(f"Creating GitHub release: {release_name}")
    release_url = f"https://github.com/{repo_fullname}/releases/tag/{release_name}"
    print(f"Preview at: {release_url}")

    gh = Github(auth=Auth.Token(github_token))

    try:
        repo = gh.get_repo(repo_fullname)
    except GithubException as e:
        print(f"Error: Could not access repository {repo_fullname}")
        print(f"Details: {e}")
        sys.exit(1)

    # Check if release already exists
    try:
        existing_release = repo.get_release(release_name)
        print(f"✅ Release {release_name!r} already exists: {existing_release.html_url}")
        return
    except GithubException as e:
        if e.status == 404:
            pass  # Release doesn't exist, continue to create
        else:
            print(f"Error: Failed to check release")
            print(f"Details: {e}")
            sys.exit(1)

    # Check if tag exists, create if not
    try:
        repo.get_git_ref(f"tags/{release_name}")
        print(f"Tag {release_name!r} already exists")
    except GithubException as e:
        if e.status == 404:
            print(f"Creating tag {release_name!r}...")
            default_branch = repo.default_branch
            commit = repo.get_branch(default_branch).commit
            commit_sha = commit.sha

            # Create annotated tag
            tag = repo.create_git_tag(
                tag=release_name,
                message=f"Release {release_name}",
                object=commit_sha,
                type="commit",
            )
            # Create tag reference
            repo.create_git_ref(
                ref=f"refs/tags/{release_name}",
                sha=tag.sha,
            )
            print(f"✅ Created tag {release_name!r} on {default_branch} ({commit_sha[:7]})")
        else:
            print(f"Error: Failed to check tag")
            print(f"Details: {e}")
            sys.exit(1)

    # Create release
    try:
        release = repo.create_git_release(
            tag=release_name,
            name=release_name,
            message=f"Release {release_name}",
        )
        print(f"✅ Successfully created release: {release.html_url}")
    except GithubException as e:
        print(f"Error: Failed to create release")
        print(f"Details: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
