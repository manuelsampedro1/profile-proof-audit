# AGENTS.md

## Goal

`profile-proof-audit` is a local-first CLI that audits GitHub profile README proof quality before public claims change.

## Constraints

- Keep the tool dependency-free and runnable from checkout.
- Do not add network calls unless they are behind `--check-http`.
- Do not assert profile-quality claims that the CLI cannot detect or report.
- Keep generated packaging metadata out of version control.
- Treat broken links, missing proof sections, and unsupported guarantees as review blockers.

## Verification

Run these before committing:

```sh
make test
make lint
make build
make smoke
git diff --check
```

## Commit Expectations

- Keep changes small and reviewable.
- Include fixture or test coverage for behavior changes.
- Leave the working tree clean after generated files are removed.
