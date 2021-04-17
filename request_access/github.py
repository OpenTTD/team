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
            f"Requesting membership returned error code {response.status_code}; JSON that followed: ",
            response.text,
        )

    return response.status_code == 200


def list_teams():
    """List all the teams known to the organisation"""
    github_token = os.getenv("GITHUB_TOKEN")

    headers = {
        "Authorization": f"bearer {github_token}",
        "Accept": "application/json",
    }

    response = requests.get("https://api.github.com/orgs/OpenTTD/teams?per_page=100", headers=headers)
    if response.status_code >= 300:
        raise Exception(
            f"Posting a reply returned error code {response.status_code}; JSON that followed: ",
            response.text,
        )

    teams = response.json()
    for team in teams:
        members = requests.get(f"https://api.github.com/orgs/OpenTTD/teams/{team['slug']}/members", headers=headers)
        if response.status_code == 200:
            team["members"] = members.json()

    return teams


def add_to_team(login, team):
    """Add a member to a team"""
    github_token = os.getenv("GITHUB_TOKEN")

    headers = {
        "Authorization": f"bearer {github_token}",
        "Accept": "application/json",
    }

    response = requests.put(f"https://api.github.com/orgs/OpenTTD/teams/{team}/memberships/{login}", headers=headers)
    if response.status_code >= 300:
        raise Exception(
            f"Adding a member to a team returned error code {response.status_code}; JSON that followed: ",
            response.text,
        )


def create_team(name, description, parent_id):
    """Create a new team, with no members"""
    github_token = os.getenv("GITHUB_TOKEN")

    payload = {
        "name": name,
        "description": description,
        "parent_team_id": parent_id,
    }

    headers = {
        "Authorization": f"bearer {github_token}",
        "Accept": "application/json",
    }

    response = requests.post("https://api.github.com/orgs/OpenTTD/teams", json=payload, headers=headers)
    if response.status_code >= 300:
        raise Exception(
            f"Creating a team returned error code {response.status_code}; JSON that followed: ",
            response.text,
        )

    # After creating a team, the user doing it is part of the team. This is
    # unwanted in our case, so we remove the user again.
    slug = response.json()["slug"]
    response = requests.get(f"https://api.github.com/orgs/OpenTTD/teams/{slug}/members", headers=headers)
    if response.status_code >= 300:
        raise Exception(
            f"Listing members of the newly created team returned error code {response.status_code}; "
            "JSON that followed: ",
            response.text,
        )

    for member in response.json():
        response = requests.delete(
            f"https://api.github.com/orgs/OpenTTD/teams/{slug}/memberships/{member['login']}", headers=headers
        )
        if response.status_code >= 300:
            raise Exception(
                f"Removing member of the newly created team returned error code {response.status_code}; "
                "JSON that followed: ",
                response.text,
            )


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
            f"Posting a reply returned error code {response.status_code}; JSON that followed: ",
            response.text,
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
            f"Posting a reply returned error code {response.status_code}; JSON that followed: ",
            response.text,
        )
