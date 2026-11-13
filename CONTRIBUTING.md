# Contributing a flow

Thanks for sharing. A flow you add here can be installed by anyone, by people who did not write it and may not read it closely, so the rules below are strict on purpose.

## Three ways to submit

1. **Issue form (easiest).** In NexFlow, export the flow, then [fill in the form](https://github.com/ADSFAaron/nexflow-flow-store/issues/new?template=submit-flow.yml) and paste the file. A bot checks it, moves personal values into install-time fields, and opens a pull request credited to you. Edit the issue to fix problems; the check runs again.
2. **From the app.** A coming NexFlow version adds "Submit to store", which prepares the same thing and opens the form for you.
3. **Pull request.** Add `flows/<slug>/flow.json` and `flows/<slug>/meta.json` yourself (format below). The `validate` check comments on your pull request with what it found.

**Whatever you paste into an issue is public**, even after you edit it. Remove Wi-Fi names, phone numbers, places and tokens before you paste.

## What a flow folder holds

```
flows/<slug>/
  flow.json   the flow, exactly as NexFlow exports it, with personal values left empty
  meta.json   title, description, tags, and the fields the installer fills in
```

Nothing else goes in the folder. The store's web pages are generated from these two files.

### `meta.json`

```json
{
  "slug": "home-wifi-ringer",
  "version": 1,
  "languages": {
    "en":    { "title": "Ringer on at home", "description": "…" },
    "zh-TW": { "title": "到家開啟鈴聲",       "description": "…" }
  },
  "tags": ["home", "wifi"],
  "setup": [
    {
      "id": "home_wifi",
      "target": { "kind": "trigger", "item": "<the trigger's id in flow.json>", "key": "ssid" },
      "label": { "en": "Your home Wi-Fi name", "zh-TW": "家裡的 Wi-Fi 名稱" },
      "secret": false
    }
  ]
}
```

- **`slug`** equals the folder name: 3–50 lowercase letters, digits or hyphens. It is permanent: it cannot be renamed, and a removed slug can never be used again.
- **`version`** starts at 1. Any change to either file must raise it.
- **`languages`**: at least one of `en`, `zh-TW`, `zh-CN`, `ja`. Title at most 60 characters, description at most 2000. The app shows the user's language, or falls back and says which language it is showing.
- **`tags`**: at most 10, lowercase.
- **`setup`**: each entry takes over one setting of one step. The installer fills it in; in `flow.json` that setting is `""`. Every label needs every language in `languages`. Mark API keys and tokens `"secret": true` so the app hides them.
- **No author field.** The store credits whoever first committed the flow, from their GitHub account.

## The rules

The `validate` check enforces these with NexFlow's own code. You can run it yourself: build `flow-store-tools` from the NexFlow repository and run `flow-store-tools validate --repo . --catalog docs/flow-catalog.json`.

- **Only what the app has.** Every trigger, condition, action and setting must exist in NexFlow, with an allowed value. The store works out the oldest app version and which builds (GitHub, Google Play) can run it.
- **Arrives off.** `"enabled": false` in `flow.json`. The user switches it on.
- **Personal values are never in the flow.** Wi-Fi names, Bluetooth devices, places, phone numbers, contacts, NFC tags, apps, app shortcuts, screen coordinates, file paths, images and HTTP headers are either empty or a `setup` field, and never a `{{variable}}`.
- **Data from strangers stays contained.** Anything a trigger hands the flow (an SMS or notification text, a caller's number) and anything a web request returns may not reach a setting that sends, calls, opens or writes.
- **Web addresses are fixed.** `https://` and a public host name, written out, not built from variables. No `localhost`, private or local network addresses, or raw IP addresses. Or leave the whole address to the installer as a `setup` field.
- **Global variables:** only ones the flow declares itself. The app renames them per install so two flows never share one by accident.
- **Limits:** loops repeat at most 100 times; regular expressions stay short.

A flow that sends SMS, makes calls, taps the screen or talks to a web server can be accepted; the store lists those actions on its page and in the app before anyone installs it. What gets refused is a flow that hides what it does.

## Your rights

You must have written the flow or have the right to share it. Don't copy templates from other automation apps. By submitting, you dedicate the flow to the public domain under [CC0 1.0](LICENSE).

## Changing someone else's flow

Allowed, through the same check. The original author is mentioned on the pull request; a maintainer decides without waiting for them.

## Review

A maintainer reviews every pull request, including ones the check passes. Workflows under `.github/` are changed only by maintainers.
