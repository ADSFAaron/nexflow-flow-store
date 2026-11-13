"""Turn a "Submit a flow" issue into the files of a pull request.

    prepare  read the issue body from $ISSUE_BODY, write the flow into a copy of the store,
             and record what happened in <out>/info.json
    comment  combine info.json with the validation report into the issue comment

The issue body is untrusted. It reaches this script only through an environment variable, never
through `${{ }}` in a shell line, and nothing in it is ever executed: it is parsed as Markdown
sections and JSON, and the one value that becomes a path (the slug) must match the slug pattern
first.

Run with `python3 -I`, from the default branch's checkout.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys

SLUG = re.compile(r"^[a-z0-9-]{3,50}$")
LANGUAGES = ["en", "zh-TW", "zh-CN", "ja"]
MAX_BODY = 200_000

# Labels in .github/ISSUE_TEMPLATE/submit-flow.yml. Keep them in step.
FIELD_SLUG = "Slug"
FIELD_LANGUAGE = "Language"
FIELD_TITLE = "Title"
FIELD_DESCRIPTION = "Description"
FIELD_TAGS = "Tags"
FIELD_FLOW = "Flow"

NO_RESPONSE = "_No response_"


def sections(body):
    """Issue forms render each field as `### Label` followed by its value."""
    found = {}
    current = None
    lines = []
    for line in body.splitlines():
        if line.startswith("### "):
            if current is not None:
                found[current] = "\n".join(lines).strip()
            current = line[4:].strip()
            lines = []
        elif current is not None:
            lines.append(line)
    if current is not None:
        found[current] = "\n".join(lines).strip()
    return {k: ("" if v == NO_RESPONSE else v) for k, v in found.items()}


def unfence(text):
    """A `render: json` textarea arrives wrapped in a code fence."""
    m = re.match(r"^```[a-zA-Z]*\n(.*)\n```$", text.strip(), re.S)
    return m.group(1) if m else text


def write_json(path, value):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write("\n")


def copy_store(store, candidate):
    """The store's content without .git or .github: what validate needs to compare against."""
    if os.path.exists(candidate):
        shutil.rmtree(candidate)
    os.makedirs(candidate)
    for name in ("flows", "revoked.json", "featured.json", "maintainers.json"):
        src = os.path.join(store, name)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(candidate, name))
        elif os.path.isfile(src):
            shutil.copy(src, os.path.join(candidate, name))
    os.makedirs(os.path.join(candidate, "flows"), exist_ok=True)


def previous_version(store, slug):
    try:
        with open(os.path.join(store, "flows", slug, "meta.json"), encoding="utf-8") as f:
            version = json.load(f).get("version")
            return version if isinstance(version, int) else None
    except (OSError, ValueError):
        return None


def prepare(args):
    info = {"slug": None, "kind": None, "update": False, "personal_keys": [], "error": None}

    def fail(message):
        info["error"] = message
        write_json(os.path.join(args.out, "info.json"), info)
        return 0

    body = os.environ.get("ISSUE_BODY", "")
    if len(body) > MAX_BODY:
        return fail("The issue is too long to be a flow.")
    fields = sections(body)
    raw = unfence(fields.get(FIELD_FLOW, ""))
    if not raw.strip():
        return fail("The **Flow** field is empty. Paste the flow file exported from NexFlow.")
    try:
        data = json.loads(raw)
    except ValueError as e:
        return fail(f"The **Flow** field is not valid JSON ({e.msg}, line {e.lineno}). "
                    "Paste the whole exported file, unchanged.")
    if not isinstance(data, dict):
        return fail("The **Flow** field must be a JSON object.")

    copy_store(args.store, args.candidate)

    if isinstance(data.get("meta"), dict) and isinstance(data.get("flow"), dict):
        # A submission package from the app's "Submit to the store": already in store form.
        info["kind"] = "package"
        slug = data["meta"].get("slug")
        if not isinstance(slug, str) or not SLUG.match(slug):
            return fail("The package's slug must be 3–50 lowercase letters, digits or hyphens.")
        info["slug"] = slug
        folder = os.path.join(args.candidate, "flows", slug)
        info["update"] = os.path.isdir(folder)
        shutil.rmtree(folder, ignore_errors=True)
        write_json(os.path.join(folder, "flow.json"), data["flow"])
        write_json(os.path.join(folder, "meta.json"), data["meta"])
    elif "triggers" in data and "actions" in data:
        # An ordinary .flow export: the form says what to call it.
        info["kind"] = "export"
        slug = fields.get(FIELD_SLUG, "").strip()
        if not SLUG.match(slug):
            return fail("**Slug** must be 3–50 lowercase letters, digits or hyphens, such as `quiet-at-night`.")
        info["slug"] = slug
        language = fields.get(FIELD_LANGUAGE, "").strip()
        if language not in LANGUAGES:
            return fail(f"**Language** must be one of {', '.join(LANGUAGES)}.")
        title = fields.get(FIELD_TITLE, "").strip()
        if not title:
            return fail("**Title** is required.")

        folder = os.path.join(args.candidate, "flows", slug)
        info["update"] = os.path.isdir(folder)
        shutil.rmtree(folder, ignore_errors=True)
        export = os.path.join(args.out, "export.flow")
        write_json(export, data)
        setup = os.path.join(args.out, "setup.json")
        run = subprocess.run(
            [args.tools, "from-export", "--export", export, "--slug", slug, "--lang", language,
             "--repo", args.candidate, "--json", setup],
            capture_output=True, text=True,
        )
        if run.returncode != 0:
            return fail("The flow file could not be read: " + run.stdout.strip().splitlines()[-1][:300]
                        if run.stdout.strip() else "The flow file could not be read.")
        with open(setup, encoding="utf-8") as f:
            info["personal_keys"] = sorted({s["target"]["key"] for s in json.load(f)})

        meta_path = os.path.join(folder, "meta.json")
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
        meta["languages"] = {language: {"title": title, "description": fields.get(FIELD_DESCRIPTION, "").strip()}}
        tags = [t.strip().lower() for t in fields.get(FIELD_TAGS, "").split(",") if t.strip()]
        if tags:
            meta["tags"] = tags
        before = previous_version(args.store, slug)
        if before is not None:
            meta["version"] = before + 1
        write_json(meta_path, meta)
    else:
        return fail("The **Flow** field is neither a NexFlow flow file nor a store submission package.")

    write_json(os.path.join(args.out, "info.json"), info)
    return 0


def comment(args):
    with open(args.info, encoding="utf-8") as f:
        info = json.load(f)
    report = ""
    if args.report and os.path.exists(args.report):
        with open(args.report, encoding="utf-8") as f:
            report = f.read()

    out = ["<!-- flow-store-submission -->"]
    if info.get("error"):
        out.append("### ❌ This submission could not be read")
        out.append("")
        out.append(info["error"])
        out.append("")
        out.append("Edit the issue to fix it; the check runs again on every edit.")
        return print("\n".join(out))

    personal = info.get("personal_keys") or []
    if personal or "personal data" in report:
        out.append("> [!WARNING]")
        out.append("> **This issue is public, and the flow you pasted contains personal values**" +
                   (" (" + ", ".join(f"`{k}`" for k in personal) + ")" if personal else "") + ".")
        out.append("> The pull request leaves them out and asks for them at install time instead, "
                   "but they are still visible here. Edit the issue and remove them, and treat them "
                   "as already seen (for example, change a token).")
        out.append("")

    out.append(report.replace("<!-- flow-store-validate -->", "").strip())
    out.append("")
    if args.ok == "true":
        verb = "update" if info.get("update") else "add"
        out.append(f"A pull request to {verb} `{info['slug']}` will open shortly. "
                   "A maintainer reviews it before it reaches the store.")
    else:
        out.append("No pull request was opened. Edit the issue to fix the problems; "
                   "the check runs again on every edit.")
    print("\n".join(out))


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command", required=True)
    a = sub.add_parser("prepare")
    a.add_argument("--store", required=True)
    a.add_argument("--candidate", required=True)
    a.add_argument("--tools", required=True)
    a.add_argument("--out", required=True)
    c = sub.add_parser("comment")
    c.add_argument("--info", required=True)
    c.add_argument("--report")
    c.add_argument("--ok", default="false")
    args = p.parse_args()
    sys.exit(prepare(args) if args.command == "prepare" else comment(args))


if __name__ == "__main__":
    main()
