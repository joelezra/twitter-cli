"""Integration smoke tests for twitter-cli.

These tests invoke the real CLI commands with ``--yaml`` against the live
Twitter/X API using your local browser cookies.  They are **skipped by
default** and only run when explicitly requested::

    uv run pytest -m smoke -v

Only read-only operations are tested — no writes.
"""

from __future__ import annotations

import yaml
import pytest
from click.testing import CliRunner

from twitter_cli.cli import cli

smoke = pytest.mark.smoke

runner = CliRunner()


def _invoke(*args: str):
    """Run a CLI command with --yaml and return parsed payload."""
    result = runner.invoke(cli, [*args, "--yaml"])
    if result.output:
        payload = yaml.safe_load(result.output)
    else:
        payload = None
    return result, payload


# ── Auth ────────────────────────────────────────────────────────────────


@smoke
class TestAuth:
    """Verify authentication is working end-to-end."""

    def test_status(self):
        result, payload = _invoke("status")
        assert result.exit_code == 0, f"status failed: {result.output}"
        assert payload["ok"] is True
        assert payload["data"]["authenticated"] is True
        assert payload["data"]["user"]["username"]

    def test_whoami(self):
        result, payload = _invoke("whoami")
        assert result.exit_code == 0, f"whoami failed: {result.output}"
        assert payload["ok"] is True
        assert payload["data"]["user"]["username"]
        assert payload["data"]["user"]["id"]


# ── Read-only queries ───────────────────────────────────────────────────


@smoke
class TestReadOnly:
    """Read-only CLI smoke tests."""

    def test_user(self):
        result, payload = _invoke("user", "elonmusk")
        assert result.exit_code == 0, f"user failed: {result.output}"
        assert payload["ok"] is True

    def test_search(self):
        result, payload = _invoke("search", "python", "--max", "3")
        assert result.exit_code == 0, f"search failed: {result.output}"
        assert payload["ok"] is True
        items = payload["data"]
        assert isinstance(items, list)
        assert len(items) >= 1

    def test_user_posts(self):
        result, payload = _invoke("user-posts", "elonmusk", "--max", "3")
        assert result.exit_code == 0, f"user-posts failed: {result.output}"
        assert payload["ok"] is True

    def test_feed(self):
        result, payload = _invoke("feed", "--max", "3")
        assert result.exit_code == 0, f"feed failed: {result.output}"
        assert payload["ok"] is True

    def test_search_with_filters(self):
        result, payload = _invoke(
            "search", "python", "--lang", "en", "--min-likes", "5", "--max", "3"
        )
        assert result.exit_code == 0, f"advanced search failed: {result.output}"
        assert payload["ok"] is True
        items = payload["data"]
        assert isinstance(items, list)
        assert len(items) >= 1


# ── Anti-detection bootstrap ────────────────────────────────────────────


@smoke
class TestClientTransaction:
    """x.com only embeds the ondemand.s bundle reference in the authenticated
    web shell.  When X reshapes that shell again, this fails here rather than
    silently dropping the x-client-transaction-id header in production.
    """

    def test_transaction_id_header_is_generated(self):
        from twitter_cli import auth
        from twitter_cli.client import TwitterClient

        cookies = auth.get_cookies()
        client = TwitterClient(
            cookies["auth_token"],
            cookies["ct0"],
            cookie_string=cookies.get("cookie_string"),
        )

        assert client._client_transaction is not None, (
            "ClientTransaction failed to bootstrap against the live x.com web shell"
        )

        headers = client._build_headers(
            url="https://x.com/i/api/graphql/abc/SearchTimeline", method="POST"
        )
        assert headers.get("X-Client-Transaction-Id")
