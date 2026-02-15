# Developer Utility Toolkit

[![CI](https://github.com/artenisalija/developer-utility-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/artenisalija/developer-utility-kit/actions/workflows/ci.yml)
[![Security](https://github.com/artenisalija/developer-utility-kit/actions/workflows/security.yml/badge.svg)](https://github.com/artenisalija/developer-utility-kit/actions/workflows/security.yml)
[![Coverage](https://img.shields.io/badge/coverage-85%25%2B-brightgreen)](https://github.com/artenisalija/developer-utility-kit)

Security-focused, modular, format-aware Python CLI for common developer tasks.

## Features

- Automatic input detection for text, JSON, XML, Base64, URL, and file extension types
- Direct format conversion using a plugin-based transformer registry
- JSON and XML formatting, minification, and validation
- Encoding tools (Base64 and URL encode/decode)
- Image pixelation utility (optional `pillow`)
- Sitemap generator and sitemap fetcher with URL validation and request timeouts
- Local command history (`~/.developer_utility_toolkit/history/history.jsonl`)

## Architecture

- `src/toolkit/core`: abstractions, registry, detector, and safe I/O helpers
- `src/toolkit/transformers`: pluggable one-step transformers
- `src/toolkit/formatters`: JSON/XML format/minify/validate services
- `src/toolkit/image_tools`: image utilities
- `src/toolkit/web_tools`: sitemap generation/fetching
- `src/toolkit/history`: local history service
- `src/toolkit/cli.py`: Typer entrypoint and command wiring

Design choices:
- No chained transformations by default (one direct transform per request target)
- Safe XML parsing via `defusedxml`
- Controlled output writes via sanitized filename + output directory constraints
- Clear failure modes with explicit non-zero exit codes

## Installation

```bash
python -m pip install --upgrade pip
pip install developer-utility-toolkit
```

Install all optional features:

```bash
pip install "developer-utility-toolkit[all]"
```

Install developer tooling:

```bash
pip install ".[all,dev]"
```

## Usage

```bash
toolkit analyze --text '{"name":"dev"}'
toolkit convert --from text --to base64 --text "hello"
toolkit format --kind json --text '{"b":2,"a":1}'
toolkit validate --kind xml --text '<root><a>1</a></root>'
toolkit minify --kind json --text '{"b":2,"a":1}'
toolkit image pixelate --input-file ./input.png --output-name output.png
toolkit sitemap generate --base-url https://example.com --path / --path /docs
toolkit sitemap fetch --url https://example.com/sitemap.xml
toolkit recent show --limit 10
```

## Security Philosophy

- Secure defaults and explicit input validation
- Defused XML parser to prevent XXE/entity expansion attacks
- No `eval`/`exec` usage
- Timeout-controlled network calls
- Sanitized output file names with constrained output directories
- Graceful errors with explicit status codes

## Development

Run local quality gates:

```bash
ruff check .
black --check .
mypy src tests
pytest
bandit -r src -ll
pip-audit --strict
safety check --full-report
```

Pre-commit:

```bash
pre-commit install
pre-commit run --all-files
```

## CI/CD

- `ci.yml`: lint + format + mypy + tests + coverage (>=85%) on Python 3.11/3.12
- `security.yml`: Bandit + pip-audit + Safety
- `release.yml`: runs on version tags (`v*.*.*`), builds wheel/sdist, runs tests, publishes to PyPI, creates GitHub release notes
- Dependabot enabled for Python packages and GitHub Actions
