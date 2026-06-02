# Profile Proof Audit

Audit a GitHub profile README for proof quality, required sections, and broken links.

Strong AI-builder profiles should not rely on vibes. They should state clear claims, link to real artifacts, and avoid promoting local-only work as public proof. `profile-proof-audit` reads a Markdown profile surface and produces a small report with issues, warnings, link checks, and a proof score.

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
python3 -m pip install --upgrade pip
python3 -m pip install -e .
```

Or run without installing:

```sh
PYTHONPATH=src python3 -m profile_proof_audit ../goal-quiero-que-me-crees-un/README.md
```

## Usage

```sh
PYTHONPATH=src python3 -m profile_proof_audit README.md
PYTHONPATH=src python3 -m profile_proof_audit README.md --check-http
PYTHONPATH=src python3 -m profile_proof_audit README.md --format json
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
make test
make lint
make build
make smoke
```

## Fit With The Agent Workflow Stack

- `profile-proof-audit`: audit the public profile surface.
- `agent-publish-queue`: audit local repos before promoting them.
- `flagship-repo-proof-packet`: strengthen one repo before featuring it.
- `public-surface-sync`: verify artifact indexes and README latest links stay synchronized.
