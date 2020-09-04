from .github import (
    issue_comment,
    issue_close,
)


def _get_request_from_body(body):
    """
    Get the request tag from the first line.

    It should be something like: <!-- REQUEST_TYPE: REQUEST_VALUE -->
    """

    first_line = body.split("\n")[0].strip()
    if not first_line.startswith("<!-- ") or not first_line.endswith(" -->"):
        return False, False

    request_type, _, request_value = first_line[5:-4].partition(":")
    return request_type, request_value.strip()


def _issue_is_modified(data):
    issue_comment(
        data["issue"]["comments_url"],
        "template_modified",
        replacement={
            "$USER$": data["issue"]["user"]["login"],
        },
    )
    issue_close(data["issue"]["url"])


def validate_issue_and_get_request(data):
    """Validate the issue body and return what request this is."""

    # Validate we can find the request tag in the body.
    body = data["issue"]["body"]
    request_type, request_value = _get_request_from_body(body)
    if request_type is False or request_type not in ("translator",):
        _issue_is_modified(data)
        return

    # Check how the body should look like.
    with open(f".github/ISSUE_TEMPLATE/{request_type}_{request_value}.md") as f:
        expected_body = f.read()

    # Skip till the first <!--, as that indicate the start of the template.
    expected_body = expected_body[expected_body.find("<!--") :]
    # Ignore everything after the "<!-- Please do not edit the above message",
    # as that allows the user to add a personal message after the important
    # bits.
    expected_body = expected_body[: expected_body.find("<!-- Please do not edit the above message")]

    # The body of an issue can be with \r\n line ending
    if not body.replace("\r\n", "\n").startswith(expected_body):
        _issue_is_modified(data)
        return

    return request_type, request_value
