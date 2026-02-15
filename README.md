# Developer Utility Toolkit

[![CI](https://github.com/artenisalija/developer-utility-kit/actions/workflows/ci.yml/badge.svg?branch=main&event=push)](https://github.com/artenisalija/developer-utility-kit/actions/workflows/ci.yml?query=branch%3Amain)
[![Security](https://github.com/artenisalija/developer-utility-kit/actions/workflows/security.yml/badge.svg?branch=main&event=push)](https://github.com/artenisalija/developer-utility-kit/actions/workflows/security.yml?query=branch%3Amain)
[![GHCR](https://github.com/artenisalija/developer-utility-kit/actions/workflows/ghcr.yml/badge.svg?branch=main&event=push)](https://github.com/artenisalija/developer-utility-kit/actions/workflows/ghcr.yml?query=branch%3Amain)
[![Coverage](https://img.shields.io/badge/coverage-85%25%2B-brightgreen)](https://github.com/artenisalija/developer-utility-kit)

Security-focused, modular, format-aware Python CLI for common developer tasks.

## Features

- Automatic input detection for text, JSON, XML, binary, hex, base64, URL, and file extension types
- Direct format conversion via transformer registry (no hidden chained conversion)
- Guided interactive mode: select input format, choose conversion mode (`all`, `one`, `multiple`), view formatted outputs
- Conversion commands: `convert`, `convert-all`, `formats`
- JSON/XML formatting, minification, and validation
- Encoding utilities: binary, hex, base64, URL encoding/decoding
- Hash and checksum reporting with `hash-all` and `interactive`
- Image pixelation utility (optional `pillow`)
- Sitemap generator and fetcher with URL validation and request timeouts
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

Install from PyPI:

```bash
python -m pip install --upgrade pip
pip install developer-utility-toolkit
```

Install with all optional features:

```bash
pip install "developer-utility-toolkit[all]"
```

Install isolated with `pipx` (recommended for CLI tools):

```bash
pipx install developer-utility-toolkit
```

## Docker (Alternative Install)

Install via GitHub Packages container (GHCR):

```bash
docker pull ghcr.io/artenisalija/developer-utility-kit:latest
```

Run help:

```bash
docker run --rm ghcr.io/artenisalija/developer-utility-kit:latest --help
```

Run a command with mounted files:

```bash
docker run --rm -v "$PWD:/work" -w /work ghcr.io/artenisalija/developer-utility-kit:latest format --kind json --file input.json --output output.json
```

Install developer tooling:

```bash
pip install ".[all,dev]"
```

## Usage

```bash
toolkit --help
toolkit formats
toolkit analyze --text '{"name":"dev"}'
toolkit convert --from text --to base64 --text "hello"
toolkit convert-all --text "hello" --from text
toolkit convert-all --text "11111111" --from binary
toolkit convert-all --text "hello" --ask
toolkit interactive
toolkit hash-all --text "hello"
toolkit hash-all --text "01101000 01101001" --from binary
toolkit hash-all --text "68656c6c6f" --from hex
toolkit format --kind json --text '{"b":2,"a":1}'
toolkit validate --kind xml --text '<root><a>1</a></root>'
toolkit minify --kind json --text '{"b":2,"a":1}'
toolkit image pixelate --input-file ./input.png --output-name output.png
toolkit sitemap generate --base-url https://example.com --path / --path /docs
toolkit sitemap fetch --url https://example.com/sitemap.xml
toolkit recent show --limit 10
```

## Interactive Flow

`toolkit interactive` asks for:
- Input format (number or letter)
- Input value
- Conversion mode:
  - `All formats`
  - `One format`
  - `Multiple formats` (comma-separated choices)

Then it prints:
- Structured conversion output blocks
- Full hash/checksum report for the input bytes

## Hash/Checksum Algorithms

`toolkit hash-all` and `toolkit interactive` report:
- MD2 Hash Generator
- MD4 Hash Generator
- MD5 Hash Generator
- NTLM Hash Generator
- SHA1 Hash Generator
- SHA2 Hash Generator
- SHA224 Hash Generator
- SHA256 Hash Generator
- SHA384 Hash Generator
- SHA512 Hash Generator
- SHA512/224 Hash Generator
- SHA512/256 Hash Generator
- SHA3-224 Hash Generator
- SHA3-256 Hash Generator
- SHA3-384 Hash Generator
- SHA3-512 Hash Generator
- CRC-16 Hash Generator
- CRC-32 Hash Generator
- Shake-128 Hash Generator
- Shake-256 Hash Generator
- MD6 Hash Generator
- Whirlpool Hash Generator
- Checksum Calculator

Note: algorithm availability depends on Python/OpenSSL build. Unsupported algorithms are marked as unavailable at runtime.

## Binary Input Notes

- Binary input accepts `0`/`1` with optional spaces.
- Non-8-bit lengths are accepted and left-padded to full bytes (`1010` becomes `00001010`).
- If one conversion target fails (for example, binary bytes are not valid UTF-8 text), other targets still continue in `convert-all` and `interactive`.

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
- `ghcr.yml`: builds and publishes multi-arch Docker images to GHCR (`ghcr.io/artenisalija/developer-utility-kit`)
- Dependabot enabled for Python packages and GitHub Actions

## Update

```bash
pip install -U developer-utility-toolkit
```
