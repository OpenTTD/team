import os
import requests


def is_part_of_team(login, team):
    """Check if a user is part of a team"""
    github_token = os.getenv("GITHUB_TOKEN")

    headers = {
        "Authorization": f"bearer {github_token}",
        "Accept": "application/json",
    }

    response = requests.get(f"https://api.github.com/orgs/OpenTTD/teams/{team}/memberships/{login}", headers=headers)
    if response.status_code not in (200, 404):
        raise Exception(
            f"Requesting membership returned error code {response.status_code}; JSON that followed: ", response.text,
        )

    return response.status_code == 200


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
