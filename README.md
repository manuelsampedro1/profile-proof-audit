# Profile Proof Audit

Audit a GitHub profile README for proof quality, required sections, and broken links.

Strong AI-builder profiles should not rely on vibes. They should make clear claims, link to real artifacts, and avoid promoting local-only work as public proof. `profile-proof-audit` reads a Markdown profile surface and produces a small report with issues, warnings, link checks, and a proof score.

## What It Checks

- Required sections such as `Current Focus`, `Selected Work`, `Latest Proof`, and `Principles`.
- Markdown links, including local relative files.
- Optional HTTP status for public links.
- Selected Work table shape.
- Latest Proof section freshness signals.
- Risky phrasing such as fake guarantees or unsupported "production-ready" claims.

The tool is dependency-free and local-first. It does not edit your profile or create GitHub repos.

## Install

```sh
python -m pip install --upgrade pip
python -m pip install -e .
```

Or run without installing:

```sh
PYTHONPATH=src python -m profile_proof_audit ../goal-quiero-que-me-crees-un/README.md
```

## Usage

```sh
profile-proof-audit README.md
profile-proof-audit README.md --check-http
profile-proof-audit README.md --format json
```

## Example Output

```md
# Profile Proof Audit

Score: 92/100

## Issues

- Missing local file for link `./recipes/missing.md`.

## Warnings

- Selected Work has fewer than 3 rows.
```

## Development

```sh
PYTHONPATH=src python -m unittest discover -s tests
PYTHONPATH=src python -m profile_proof_audit examples/profile.md --format json
```

## Fit With The Agent Workflow Stack

- `profile-proof-audit`: audit the public profile surface.
- `agent-publish-queue`: audit local repos before promoting them.
- `flagship-repo-proof-packet`: strengthen one repo before featuring it.
- `public-surface-sync`: verify artifact indexes and README latest links stay synchronized.
