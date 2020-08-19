import requests

from .github import (
    create_team,
    list_teams,
)


def do_generate_issue_templates():
    # TODO -- Validate if the teams exists in GitHub; create them otherwise

    response = requests.get("https://translator.openttd.org/language-list")
    if response.status_code != 200:
        raise Exception("Couldn't fetch language list from translator.openttd.org")

    teams = list_teams()
    for team in teams:
        if team["name"] == "Translators":
            team_translators_id = team["id"]
            break
    else:
        raise Exception("Couldn't find Translators team on GitHub")

    github_known_teams = []
    for team in teams:
        if team["parent"] is not None and team["parent"]["id"] == team_translators_id:
            github_known_teams.append(team["name"])

    for line in response.content.decode().split("\n")[1:]:
        line = line.strip()
        if not line:
            continue

        (isocode, _, _, _, name, ownname, _, _, _) = line.split(",")

        with open("templates/issue_template_translator.md", "r") as template_fp:
            template = template_fp.read()

        with open(f".github/ISSUE_TEMPLATE/translator_{isocode}.md", "w") as lang_fp:
            lang = template
            for key, value in {"$NAME$": name, "$ISOCODE$": isocode}.items():
                lang = lang.replace(key, value)
            lang_fp.write(lang)

        if isocode not in github_known_teams:
            print(f"Creating GitHub team {isocode} ...")
            create_team(isocode, ownname, team_translators_id)
