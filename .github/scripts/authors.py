"""Work out who wrote each flow, from GitHub's records rather than anything in the files.

    python3 -I authors.py --repo OWNER/NAME SLUG [SLUG ...]   ->  {"slug": "login", ...} on stdout

A flow's author is whoever proposed the change that first put `flows/<slug>/meta.json` on the
default branch:

- that commit came from a pull request opened by a person: the person who opened it, whatever
  the merge method (a squash merge's commit is authored by the opener anyway);
- the pull request was opened by the submission App: the author of its first commit, which
  submission.yml writes as the issue's author through their noreply address;
- no pull request (a maintainer pushed it): the commit's author.

A slug whose author cannot be told is left out; build-index then records "unknown".
Needs GH_TOKEN with read access to contents and pull requests.
"""

import argparse
import json
import re
import subprocess
import sys

SLUG = re.compile(r"^[a-z0-9-]{3,50}$")


def gh(*args):
    run = subprocess.run(["gh", "api", *args], capture_output=True, text=True)
    if run.returncode != 0:
        raise RuntimeError(run.stderr.strip())
    return run.stdout


def author(repo, slug):
    shas = gh("--paginate", f"repos/{repo}/commits?path=flows/{slug}/meta.json&per_page=100",
              "-q", ".[].sha").split()
    if not shas:
        return None
    first = shas[-1]
    pulls = json.loads(gh(f"repos/{repo}/commits/{first}/pulls"))
    merged = [p for p in pulls if p.get("merged_at")]
    if merged:
        pr = merged[0]
        user = pr.get("user") or {}
        if user.get("type") != "Bot":
            return user.get("login")
        commits = json.loads(gh(f"repos/{repo}/pulls/{pr['number']}/commits?per_page=100"))
        for c in commits:
            login = (c.get("author") or {}).get("login")
            if login:
                return login
        return None
    commit = json.loads(gh(f"repos/{repo}/commits/{first}"))
    return (commit.get("author") or {}).get("login")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True)
    p.add_argument("slugs", nargs="*")
    args = p.parse_args()
    found = {}
    for slug in args.slugs:
        if not SLUG.match(slug):
            continue
        try:
            login = author(args.repo, slug)
        except (RuntimeError, ValueError) as e:
            print(f"{slug}: {e}", file=sys.stderr)
            continue
        if login:
            found[slug] = login
    json.dump(found, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
