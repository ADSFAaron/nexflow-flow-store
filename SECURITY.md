# Security

## Reporting

Report security problems with the store (the workflows, the signing, the validator, or a flow that gets past the rules) through [private vulnerability reporting](https://github.com/ADSFAaron/nexflow-flow-store/security/advisories/new). Please don't open a public issue.

A harmful flow that is already published is a moderation case: use the [report form](https://github.com/ADSFAaron/nexflow-flow-store/issues/new?template=report-flow.yml) so it is revoked as fast as possible. Problems in the NexFlow app itself go to the [NexFlow repository](https://github.com/ADSFAaron/NexFlow).

## How the store is protected

- **Review.** Every change to `master` goes through a pull request, the `validate` check, and a maintainer's approval (CODEOWNERS). Only the maintainer's own account can bypass this; GitHub Actions and the submission App cannot.
- **Workflows.** Pull requests are checked with a read-only token and no secrets. Untrusted text (issue bodies, a pull request's results) is passed through environment variables and read as data, never executed. The submission App can only write contents and pull requests; it cannot change workflows or settings.
- **Signing.** `index.json` is signed with Ed25519. The key lives in the `production` environment, which needs the maintainer's approval for every run, and the job that signs runs nothing but `openssl`. The app checks the signature, then each flow's sha256, and refuses an index older than one it has already seen.
- **Pinned tools.** Publishing builds NexFlow's validator from a fixed commit (`.github/nexflow-tools.ref`); third-party actions are pinned to commit SHAs.

## Signing keys

The app has two public keys built in: `current`, which signs today, and `next`, held in reserve. Both are in [`keys/`](keys/). Their private keys are kept offline; only `current` is also stored as the `FLOW_STORE_SIGNING_KEY` secret.

### If the signing key leaks

1. **Sign with `next` at once.** Replace the `FLOW_STORE_SIGNING_KEY` secret with the `next` private key, and in one pull request move `keys/next.pub` to `keys/current.pub`. Re-run `publish`. Apps already trust `next`, so nothing breaks.
2. **Ship an app update the same day** that removes the leaked key and adds a newly generated `next`.
3. **Commit the new `keys/next.pub`**, and store its private key offline.

**What stays exposed:** an app that has not updated still trusts the leaked key until it does. Whoever holds the key could sign a fake index for those apps, though they would also need to serve it from this repository's Pages site, or intercept the connection. The app update in step 2 is what closes this, so it cannot wait.

### Rotating without a leak

Same steps, at a calm moment: promote `next`, release an app with a new `next`, then commit it.
