
"""
Create a project on ReadTheDocs.org.

Required environment variables:
- READTHEDOCS_TOKEN: ReadTheDocs API token

The script is idempotent - it will skip if the project already exists.
"""

# ------------------------------------------------------------------------------
# Environment Variable Names
# ------------------------------------------------------------------------------
ENV_READTHEDOCS_TOKEN = "READTHEDOCS_TOKEN"

import os
import sys

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Run: uv sync --extra mise")
    sys.exit(1)

from utils import (
    get_github_repo_url,
    get_project_name,
    get_readthedocs_slug,
    get_readthedocs_url,
)


def main():
    # Get token from environment
    rtd_token = os.environ.get(ENV_READTHEDOCS_TOKEN)

    if not rtd_token:
        print(f"Error: {ENV_READTHEDOCS_TOKEN} environment variable not set")
        print("Create a token at: https://app.readthedocs.org/accounts/tokens/")
        sys.exit(1)

    project_name = get_project_name()
    project_slug = get_readthedocs_slug()
    repo_url = get_github_repo_url()
    doc_url = get_readthedocs_url()

    print(f"Setting up ReadTheDocs project: {project_name}")
    dashboard_url = f"https://app.readthedocs.org/dashboard/{project_slug}/edit/"
    print(f"Preview at: {dashboard_url}")

    headers = {
        "Accept": "application/json",
        "Authorization": f"Token {rtd_token}",
    }
    endpoint = "https://readthedocs.org/api/v3"

    # Check if project already exists (idempotent)
    check_url = f"{endpoint}/projects/{project_slug}/"
    with httpx.Client(timeout=30) as client:
        response = client.get(check_url, headers=headers)

        if response.status_code == 200:
            project_url = f"https://app.readthedocs.org/projects/{project_slug}/"
            print(f"✅ Project already exists on ReadTheDocs: {project_url}")
            return

        if response.status_code != 404:
            print(f"Error: Unexpected response from ReadTheDocs API")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            sys.exit(1)

        # Project doesn't exist, create it
        print("Project does not exist on ReadTheDocs, creating...")

        create_url = f"{endpoint}/projects/"
        data = {
            "name": project_name,
            "repository": {
                "url": repo_url,
                "type": "git",
            },
            "homepage": doc_url,
            "programming_language": "py",
            "language": "en",
            "privacy_level": "public",
            "external_builds_privacy_level": "public",
            "versioning_scheme": "multiple_versions_with_translations",
            "tags": [],
        }

        response = client.post(create_url, headers=headers, json=data)

        if 200 <= response.status_code < 300:
            print(f"✅ Successfully created project on ReadTheDocs")
            print(f"   View at: {doc_url}")
        else:
            print(f"Error: Failed to create project")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            sys.exit(1)


if __name__ == "__main__":
    main()
