# NexFlow Flow Store

[中文說明](README.zh-TW.md)

Ready-made automations for [NexFlow](https://github.com/ADSFAaron/NexFlow), shared by its users.

> **Status:** being set up. The in-app store arrives in a coming NexFlow version; until then you can read the flows here.

- **Browse:** <https://adsfaaron.github.io/nexflow-flow-store/> — a page per flow that says what it does, what it asks you to fill in, and which risky actions (SMS, calls, web requests…) it uses.
- **Install:** from the app. A store flow arrives switched off, and anything personal (your Wi-Fi name, a phone number, which app to open) is asked for at install time, never shipped in the flow.
- **Contribute:** see [CONTRIBUTING.md](CONTRIBUTING.md). You can open a pull request, or fill in an issue form and let a bot open one for you.
- **Report a flow:** [open a report](https://github.com/ADSFAaron/nexflow-flow-store/issues/new?template=report-flow.yml). What happens next is in [MODERATION.md](MODERATION.md).
- **Security problems** with the store itself: [SECURITY.md](SECURITY.md).

## How a flow gets here

1. Someone proposes it (pull request or issue form).
2. A check runs NexFlow's own validator on it: every step and setting must exist in the app, personal values must be left for the installer, data a stranger can control (an SMS body, a web reply) may not reach anything that sends or opens, web addresses must be fixed `https` hosts, and more.
3. A maintainer reviews and merges it.
4. The store is rebuilt and signed. The app checks the signature and each flow's checksum before installing anything.

## ⚠️ Do not rename this repository

The app downloads the store from `https://adsfaaron.github.io/nexflow-flow-store/`, and that address is built into every released version. Renaming this repository or the `ADSFAaron` account would break the store for every existing install, because GitHub Pages does not redirect.

## License

Flows in this repository are dedicated to the public domain under [CC0 1.0](LICENSE).
