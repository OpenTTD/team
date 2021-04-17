import requests

from .github import (
    create_team,
    list_teams,
)


def do_generate_issue_templates():
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

    github_known_teams = dict()
    for team in teams:
        if team["parent"] is not None and team["parent"]["id"] == team_translators_id:
            github_known_teams[team["name"]] = team

    for line in response.content.decode().split("\n")[1:]:
        line = line.strip()
        if not line:
            continue

        (isocode, _, _, _, name, ownname, _, _, _) = line.split(",")

        # The base language cannot be translated.
        if isocode == "en_GB":
            continue

        team = github_known_teams.get(isocode)
        template = "templates/issue_template_translator.md"
        if team and len(team.get("members", [])) >= 10:
            template = "templates/issue_template_translator_full.md"

        with open(template, "r") as template_fp:
            template = template_fp.read()

        with open(f".github/ISSUE_TEMPLATE/translator_{isocode}.md", "w") as lang_fp:
            lang = template
            for key, value in {"$NAME$": name, "$ISOCODE$": isocode}.items():
                lang = lang.replace(key, value)
            lang_fp.write(lang)

        if team is None:
            print(f"Creating GitHub team {isocode} ...")
            create_team(isocode, ownname, team_translators_id)
