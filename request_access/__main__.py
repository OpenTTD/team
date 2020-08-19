import click
import json
import os

from .issue_templates import do_generate_issue_templates
from .github import (
    add_to_team,
    is_part_of_team,
    issue_comment,
    issue_close,
)
from .validate_issue import validate_issue_and_get_request

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


def _new_issue(request_type, request_value, data):
    issue_comment(
        data["issue"]["comments_url"],
        f"request_{request_type}_pending",
        replacement={"$REQUEST_VALUE$": request_value, "$USER$": data["issue"]["user"]["login"],},
    )


def _is_core_developer(login):
    return is_part_of_team(login, "core-developers")


def _request_approve(request_type, request_value, data):
    # Silently ignore the ticket if it was already closed
    if data["issue"]["state"] != "open":
        print("This issue is already closed; ignoring approval")
        return

    # Silently ignore if the user approving is not in the right team
    if not _is_core_developer(data["comment"]["user"]["login"]):
        print("The person approving is not part of the Core Developers team")
        return

    add_to_team(data["issue"]["user"]["login"], request_value)

    issue_comment(
        data["issue"]["comments_url"],
        f"request_{request_type}_approved",
        replacement={"$REQUEST_VALUE$": request_value, "$USER$": data["issue"]["user"]["login"],},
    )
    issue_close(data["issue"]["url"])


def _request_deny(request_type, request_value, data):
    # Silently ignore the ticket if it was already closed
    if data["issue"]["state"] != "open":
        print("This issue is already closed; ignoring approval")
        return

    # Silently ignore if the user approving is not in the right team
    if not _is_core_developer(data["comment"]["user"]["login"]):
        print("The person approving is not part of the Core Developers team")
        return

    issue_comment(
        data["issue"]["comments_url"],
        f"request_{request_type}_denied",
        replacement={"$REQUEST_VALUE$": request_value, "$USER$": data["issue"]["user"]["login"],},
    )
    issue_close(data["issue"]["url"])


def _new_comment(request_type, request_value, data):
    if data["comment"]["body"].startswith("/approve"):
        _request_approve(request_type, request_value, data)
    elif data["comment"]["body"].startswith("/deny"):
        _request_deny(request_type, request_value, data)
    else:
        print("This is not a comment approving or denying the request; ignoring")


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option("--new-issue", help="Indicate there is a new issue", is_flag=True)
@click.option("--new-comment", help="Indicate there is a new comment", is_flag=True)
@click.option("--generate-issue-templates", help="Generate issue templates", is_flag=True)
def main(new_issue, new_comment, generate_issue_templates):
    if not new_issue and not new_comment and not generate_issue_templates:
        raise Exception("Please select an option")

    if os.getenv("GITHUB_TOKEN") is None:
        raise Exception("Expected GITHUB_TOKEN to be set; none found")

    if generate_issue_templates:
        do_generate_issue_templates()
        return

    with open(os.getenv("GITHUB_EVENT_PATH")) as f:
        data = json.loads(f.read())

    # Check if the "request_access" label was attached. If not, it means this
    # was not a request to process automatically. For example, a legit bug
    # with this repository.
    if not any([label["name"] == "request_access"] for label in data["issue"]["labels"]):
        print("This is not an issue to request access; ignoring")
        return

    request_type, request_value = validate_issue_and_get_request(data)

    # Comment what is happening next.
    if new_issue:
        _new_issue(request_type, request_value, data)
    elif new_comment:
        _new_comment(request_type, request_value, data)


if __name__ == "__main__":
    main()
