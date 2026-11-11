"""Turn flow-store-tools' `validate --json` output into Markdown.

Used three ways: the validate job summary, the comment report-validate.yml leaves on a pull
request, and the comment submission.yml leaves on an issue.

The JSON is untrusted. A pull request from a fork can change validate.yml and write whatever it
likes into the file, and every string in it (slugs, problems, dry-run steps) can come from a
contributor anyway. So this script only ever reads it as data, checks every type, and defangs
every string before it reaches Markdown: no mentions, no code-fence breakouts, no HTML, nothing
that could fake the marker comment, and a hard cap on size.

Run with `python3 -I`, from the default branch's checkout, never from the pull request's.
"""

import argparse
import json
import re
import sys

MARKER = "<!-- flow-store-validate -->"
MAX_ITEMS = 40
MAX_TEXT = 300
MAX_BODY = 60000

CONTROL = re.compile(r"[\x00-\x1f\x7f​-‏‪-‮⁦-⁩]")


def clean(value):
    """Untrusted text, made safe to drop into Markdown on one line."""
    if not isinstance(value, str):
        value = "" if value is None else str(value)
    value = CONTROL.sub(" ", value)
    value = value.replace("`", "'").replace("<", "‹").replace(">", "›")
    # A zero-width space after @ keeps "@someone" from notifying anyone.
    value = value.replace("@", "@​")
    # Markdown that could turn text into a link or image.
    value = value.replace("](", "] (").replace("![", "! [")
    # Bare URLs autolink; a validation problem may quote one, but the bot should not link it.
    value = value.replace("://", ":\u200b//").replace("www.", "www\u200b.")
    if len(value) > MAX_TEXT:
        value = value[:MAX_TEXT] + "…"
    return value


def strings(value):
    return [clean(v) for v in value[:MAX_ITEMS]] if isinstance(value, list) else []


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict) or not isinstance(data.get("flows"), list):
        return None
    return data


def render(data, args):
    out = [MARKER]
    if data is None:
        out.append("### ⚠️ Flow store check could not run")
        out.append("")
        out.append("The validator produced no results. A maintainer will look at the run log.")
        if args.run_url:
            out.append("")
            out.append(f"[Run log]({args.run_url})")
        return "\n".join(out)

    ok = data.get("ok") is True and all(isinstance(f, dict) and f.get("ok") is True for f in data["flows"])
    if args.conclusion and args.conclusion != "success":
        ok = False
    out.append("### " + ("✅ Flow store check passed" if ok else "❌ Flow store check found problems"))
    out.append("")

    repo_problems = strings(data.get("problems"))
    if repo_problems:
        out.append("**Repository**")
        out += [f"- {p}" for p in repo_problems]
        out.append("")

    for flow in data["flows"][:MAX_ITEMS]:
        if not isinstance(flow, dict):
            continue
        slug = clean(flow.get("slug"))
        if args.only and slug not in args.only:
            continue
        version = flow.get("version")
        version = f" v{version}" if isinstance(version, int) else ""
        if flow.get("ok") is True:
            facts = []
            if isinstance(flow.get("min_app_version"), str):
                facts.append("needs NexFlow " + clean(flow["min_app_version"]))
            flavors = strings(flow.get("flavors"))
            if flavors:
                facts.append("runs on " + ", ".join(flavors))
            risks = strings(flow.get("risks"))
            facts.append("risky actions: " + (", ".join(risks) if risks else "none"))
            out.append(f"- ✅ **{slug}**{version} — " + "; ".join(facts))
            steps = strings(flow.get("dry_run"))
            if steps and args.mode != "summary":
                out.append("  <details><summary>Dry run</summary>")
                out.append("")
                out += ["  " + "&nbsp;" * 2 * (len(s) - len(s.lstrip(" "))) + s.strip() for s in steps]
                out.append("  </details>")
        else:
            out.append(f"- ❌ **{slug}**{version}")
            out += [f"  - {p}" for p in strings(flow.get("problems"))]

    if args.owners:
        out.append("")
        out.append("This changes a flow someone else published. Original author" +
                   ("s" if len(args.owners) > 1 else "") + ": " +
                   ", ".join(f"@{o}" for o in args.owners) +
                   ". A maintainer still decides; the change does not wait for them.")

    if args.run_url:
        out.append("")
        out.append(f"[Run log]({args.run_url})")

    body = "\n".join(out)
    if len(body) > MAX_BODY:
        body = body[:MAX_BODY] + "\n\n…(cut short)"
    return body


LOGIN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("result")
    p.add_argument("--mode", choices=["summary", "comment"], default="comment")
    p.add_argument("--conclusion", default="")
    p.add_argument("--run-url", default="")
    p.add_argument("--owner", action="append", default=[],
                   help="GitHub login to mention as an original author; must come from the API, not the JSON")
    p.add_argument("--only", action="append", default=[], help="Only report these slugs")
    args = p.parse_args()
    args.owners = [o for o in args.owner if LOGIN.match(o)]
    if args.run_url and not args.run_url.startswith("https://github.com/"):
        args.run_url = ""
    sys.stdout.write(render(load(args.result), args) + "\n")


if __name__ == "__main__":
    main()
