import os
import requests


def issue_comment(comments_url, template, replacement=None):
    """Add a comment to an issue."""
    github_token = os.getenv("GITHUB_TOKEN")

    with open(f"templates/reply_{template}.md") as f:
        body = f.read()
    if replacement is not None:
        for key, value in replacement.items():
            body = body.replace(key, value)

    headers = {
        "Authorization": f"bearer {github_token}",
        "Accept": "application/json",
    }

    response = requests.post(comments_url, json={"body": body}, headers=headers)
    if response.status_code >= 300:
        raise Exception(
            f"Posting a reply returned error code {response.status_code}; JSON that followed: ", response.text,
        )


def issue_close(issue_url):
    """Close an issue."""
    github_token = os.getenv("GITHUB_TOKEN")

    headers = {
        "Authorization": f"bearer {github_token}",
        "Accept": "application/json",
    }

    response = requests.patch(issue_url, json={"state": "closed"}, headers=headers)
    if response.status_code >= 300:
        raise Exception(
            f"Posting a reply returned error code {response.status_code}; JSON that followed: ", response.text,
        )
