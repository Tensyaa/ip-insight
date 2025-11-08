# DevOps Guide (Tim)

## Branching & Protection
- Default branch: `main`
- Require PR reviews (1+)
- Require status checks: CI, Lint, CodeQL

## Local Dev
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q
flask --app app_eb_trial run
```

## CI Workflows
- `.github/workflows/python-ci.yml`: pytest
- `.github/workflows/lint.yml`: flake8
- `.github/workflows/codeql.yml`: security

## Docker
```bash
docker build -t ip-insight .
docker run --rm -p 5000:5000 ip-insight
```

## Notes
- Tests mock the external API; no internet needed.
- Handles API rate-limits & error JSON gracefully.
