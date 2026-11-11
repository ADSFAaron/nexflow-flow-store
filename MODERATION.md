# Moderation

How reports are handled and when a flow is taken down. The store has one maintainer, so these are targets, not guarantees.

## Not allowed

- Flows that do something other than what their title and description say, or hide what they do.
- Flows that send personal data anywhere the user did not choose: messages, contacts, location, notification contents, files.
- Flows meant to cost the user money (premium SMS, paid calls) or to harass someone (repeated messages or calls).
- Flows that try to get around Android's or NexFlow's protections.
- Personal information about anyone, in a flow or its description.
- Copied work you have no right to share, including other automation apps' templates.
- Spam, advertising, or hateful, sexual or violent content in titles and descriptions.

## Reports

Report a flow with the [report form](https://github.com/ADSFAaron/nexflow-flow-store/issues/new?template=report-flow.yml). Reports land on the maintainer's triage board.

| Report | Target | Action |
|---|---|---|
| Harmful or malicious | same day | Revoked as `malicious`. The app switches the flow off on every phone the next time it opens, and tells the user why. |
| Contains personal information | same day | The values are removed; the flow gets a new version. If the history must be scrubbed, GitHub support is asked. |
| Broken | 14 days for the author to fix | If still broken, revoked as `broken`. The app tells users; it does not switch the flow off. |
| Copied without permission | 7 days | Removed when the claim holds up. |
| Other | 7 days | Case by case. |

## Revoking

A maintainer revokes a flow in one pull request that does both:

1. adds `{ "slug": "…", "reason": "malicious" | "broken", "date": "YYYY-MM-DD", "note": "…" }` to `revoked.json`;
2. deletes `flows/<slug>/`.

The slug can never be used again, by anyone. Publishing the store then reaches every app that checks in.

## Repeat offenders

An author whose flow is revoked as `malicious` is blocked from the repository. Two `broken` revocations within six months get the same.

## Appeals

Open an issue saying which flow and why. A different outcome needs new information.
