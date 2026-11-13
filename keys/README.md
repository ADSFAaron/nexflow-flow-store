# Signing keys

Public halves of the Ed25519 keys that sign `index.json`. The app has both built in.

| File | Role |
|---|---|
| `current.pub` | Signs the store today. `publish` checks its signature against this file before deploying, and again after. |
| `next.pub` | Held in reserve. If `current` leaks, the store switches to `next` and nothing breaks for apps that already trust it. |

Both are PEM `SubjectPublicKeyInfo`, as `openssl pkey -pubout` writes them. The private keys never enter this repository; how they are made, stored and rotated is in [SECURITY.md](../SECURITY.md) and MAINTAINING.md.
