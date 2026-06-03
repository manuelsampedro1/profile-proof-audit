.PHONY: test lint build smoke

test:
	PYTHONPATH=src python3 -m unittest discover -s tests

lint:
	python3 -m py_compile src/profile_proof_audit/*.py tests/test_cli.py

build:
	python3 -m py_compile src/profile_proof_audit/*.py tests/test_cli.py

smoke:
	PYTHONPATH=src python3 -m profile_proof_audit examples/profile.md
	PYTHONPATH=src python3 -m profile_proof_audit examples/profile.md --format json > /tmp/profile-proof-audit.json
	PYTHONPATH=src python3 -m profile_proof_audit examples/profile.md --min-score 100 --fail-on-warnings
