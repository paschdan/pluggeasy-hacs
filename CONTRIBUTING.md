# Contribution guidelines

Contributing to this project should be as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features

## Github is used for everything

Github is used to host code, to track issues and feature requests, as well as accept pull requests.

Pull requests are the best way to propose changes to the codebase.

1. Fork the repo and create your branch from `main`.
2. If you've changed something, update the documentation.
3. Make sure your code lints (using `scripts/lint`).
4. Test your contribution.
5. Issue that pull request with a conventional commit title!

## Conventional commits and releases

Use [Conventional Commits](https://www.conventionalcommits.org/) for PR titles
and commits. The **Conventional PR title** check validates titles, including an
optional scope and breaking-change marker:

- `fix: correct climate action` produces a patch release.
- `feat(sensor): add a measurement` produces a minor release.
- `feat!: change the API` produces a major release. Explain the breaking change
  in the PR body and retain any `BREAKING CHANGE:` footer in the merge commit.
- `docs:`, `ci:`, `test:`, `chore:`, and other maintenance types do not create a
  release on their own.

Prefer **Squash and merge**, and use the conventional PR title as the squash
commit subject. If using **Rebase and merge**, every retained commit must be
conventional; the PR-title check does not validate individual commit messages.

### Release process

On pushes to `main`, **Release Please** creates or updates a release PR from
conventional commits since the previous release. It updates `CHANGELOG.md`,
`version.txt`, `.release-please-manifest.json`, and the integration's
`custom_components/pluggeasy/manifest.json` version together. Device-library
dependency pins are not changed.

Review that PR, wait for CI, and merge it to publish a `vX.Y.Z` tag and GitHub
release. HACS uses the tagged repository contents; no separate ZIP asset is
required. Releases are not published from feature branches or unmerged PRs.
The **Release** workflow can also be dispatched manually on `main` to retry.

The initial version is `0.6.4`; the bootstrap SHA points to the existing
`v0.6.4` release so older history is not included in the first changelog. The
bootstrap setting is ignored after the first release-please release.

### One-time repository setup

1. Add an Actions repository secret named `RELEASE_PLEASE_TOKEN` containing a
   fine-grained personal access token limited to this repository, with
   **Contents**, **Issues**, and **Pull requests** read/write permissions. Keep
   it out of files and rotate it before expiry.
2. Make **Conventional PR title** and the existing lint, validation, and test
   checks required in the repository's `main` branch rules.
3. Prefer the repository's squash-merge default commit title setting to
   **Pull request title**, so GitHub preserves the validated title.

A separate token is intentional: PRs and tags created using the built-in
`GITHUB_TOKEN` do not trigger other GitHub Actions workflows. Using the release
token allows CI to run on generated release PRs. The workflow fails with a
setup message if the secret is missing; it never merges release PRs itself.

## Any contributions you make will be under the MIT Software License

In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using Github's [issues](../../issues)

GitHub issues are used to track public bugs.
Report a bug by [opening a new issue](../../issues/new/choose); it's that easy!

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can.
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

People *love* thorough bug reports. I'm not even kidding.

## Use a Consistent Coding Style

Use [ruff](https://github.com/astral-sh/ruff) to make sure the code follows the style.

## Test your code modification

This custom component is based on [integration_blueprint template](https://github.com/ludeeus/integration_blueprint).

It comes with development environment in a container, easy to launch
if you use Visual Studio Code. With this container you will have a stand alone
Home Assistant instance running and already configured with the included
[`configuration.yaml`](./config/configuration.yaml)
file.

## License

By contributing, you agree that your contributions will be licensed under its MIT License.
