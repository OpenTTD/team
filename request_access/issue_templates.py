import requests


def do_generate_issue_templates():
    # TODO -- Validate if the teams exists in GitHub; create them otherwise

    response = requests.get("https://translator.openttd.org/language-list")
    if response.status_code != 200:
        raise Exception("Couldn't fetch language list from translator.openttd.org")

    for line in response.content.decode().split("\n"):
        line = line.strip()
        if not line:
            continue

        (isocode, grflangid, filename, is_stable, name, ownname, plural, gender, case) = line.split(",")

        with open("templates/issue_template_translator.md", "r") as template_fp:
            template = template_fp.read()

        with open(f".github/ISSUE_TEMPLATE/translator_{isocode}.md", "w") as lang_fp:
            lang = template
            for key, value in {"$NAME$": name, "$ISOCODE$": isocode}.items():
                lang = lang.replace(key, value)
            lang_fp.write(lang)
