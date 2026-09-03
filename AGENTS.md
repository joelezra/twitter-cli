# AGENTS.md — Agent Developer Guide for twitter-cli

This file provides context for AI agents working in this repository.

## Project Overview

- **Project**: twitter-cli — A CLI for Twitter/X (read timelines, bookmarks, search, post, reply, etc.)
- **Language**: Python 3.10+
- **Package Manager**: uv (recommended) / pip
- **Repository**: https://github.com/joelezra/twitter-cli

## Build, Lint, and Test Commands

```bash
# Install all dependencies (including dev)
uv sync --extra dev

# Run ruff linter
uv run ruff check .

# Run mypy type checker
uv run mypy twitter_cli

# Run all tests (excludes smoke tests by default)
uv run pytest -q

# Run a single test
uv run pytest tests/test_cli.py::test_feed_command -v

# Run tests matching pattern
uv run pytest -k "test_parse" -v
```

## Code Style

- **Line length**: 100 characters
- **Python version**: 3.10+
- Use `from __future__ import annotations` at top of all .py files
- **Functions/variables**: `snake_case`, **Classes**: `PascalCase`, **Constants**: `UPPER_SNAKE_CASE`
- Private functions: prefix with `_`
- Use `@dataclass` for data models (in `models.py`)
- Use Click framework for CLI commands
- Custom exceptions in `exceptions.py`, base: `TwitterError(RuntimeError)`

## Project Structure

```
twitter_cli/
├── cli.py               # Click CLI entry point
├── client.py            # Twitter API client (HTTP)
├── auth.py              # Cookie extraction & auth
├── graphql.py           # GraphQL query IDs
├── parser.py            # Tweet/User parsing
├── models.py            # Dataclass models
├── formatter.py         # Rich table formatting
├── serialization.py     # YAML/JSON output
├── output.py            # Structured output helpers
├── config.py            # Config loading
├── filter.py            # Tweet ranking/scoring
├── constants.py         # Constants
├── exceptions.py        # Custom exceptions
├── cache.py             # Tweet caching
├── search.py            # Search utilities
└── timeutil.py          # Time utilities
```

## CI

- GitHub Actions: Python 3.10, 3.11, 3.12
- CI validates: ruff check + mypy + pytest

## Working against the live X API

```bash
# Live read-only integration tests (uses your real browser cookies)
uv run pytest -m smoke -v
```

Two facts that are not visible from the code alone:

- **x.com serves two different web shells.** Authenticated requests get the
  legacy `responsive-web/client-web` app, whose inline webpack manifest carries
  the `ondemand.s` entry that `x_client_transaction` scrapes to derive the
  `x-client-transaction-id` header. Anonymous requests get a separate
  lightweight `x-web` app with no manifest at all. Anything bootstrapping
  ClientTransaction must therefore send the session cookies — see
  `TwitterClient._ensure_client_transaction`.
- **`FALLBACK_QUERY_IDS` in `graphql.py` goes stale on X's schedule.** It is a
  fast path, not a source of truth: `_graphql_get`/`_graphql_post` re-resolve
  against `fa0311/twitter-openapi` on a 404/422 and retry. Refresh the table
  from upstream `jackwener/twitter-cli` rather than hand-editing entries, and
  verify affected commands live afterwards.

Upstream is not configured as a remote. Fetch it explicitly:

```bash
git fetch https://github.com/jackwener/twitter-cli.git main:refs/remotes/upstream/main
```

## Maintaining this file

Keep this file for knowledge useful to almost every future agent session in this project.
Do not repeat what the codebase already shows; point to the authoritative file or command instead.
Prefer rewriting or pruning existing entries over appending new ones.
When updating this file, preserve this bar for all agents and keep entries concise.
