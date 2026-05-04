# twitter-cli

[![CI](https://github.com/joelezra/twitter-cli/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/joelezra/twitter-cli/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/twitter-cli.svg)](https://pypi.org/project/twitter-cli/)
[![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue.svg)](https://pypi.org/project/twitter-cli/)

A terminal-first CLI for Twitter/X. Read timelines, bookmarks, search, post, reply, quote, like, retweet, follow — all without API keys. Designed for both human use and AI agent integration.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Authentication](#authentication)
- [Commands](#commands)
- [Output Modes](#output-modes)
- [Configuration](#configuration)
- [NanoClaw Integration](#nanoclaw-integration)
- [Adding Skills](#adding-skills)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

## Installation

```bash
# Recommended: uv tool (fast, isolated)
uv tool install twitter-cli

# Alternative: pipx
pipx install twitter-cli

# From source
git clone https://github.com/joelezra/twitter-cli.git
cd twitter-cli
uv sync
```

Upgrade:

```bash
uv tool upgrade twitter-cli
```

> Upgrade regularly — Twitter rotates GraphQL query IDs frequently.

## Quick Start

```bash
# Check auth
twitter status

# Fetch your timeline
twitter feed

# Search tweets
twitter search "Claude Code" --max 20

# Post a tweet
twitter post "Hello from twitter-cli!"
```

## Authentication

Auth priority:

1. **Environment variables** — `TWITTER_AUTH_TOKEN` + `TWITTER_CT0`
2. **Browser cookies** (recommended) — auto-extracted from Arc / Chrome / Edge / Firefox / Brave

Browser extraction is recommended — it forwards ALL Twitter cookies, making requests look like normal browser traffic.

```bash
# Verify auth works
twitter whoami

# Specify Chrome profile
TWITTER_CHROME_PROFILE="Profile 2" twitter feed

# Specify browser
TWITTER_BROWSER=chrome twitter feed
```

### Proxy Support

```bash
export TWITTER_PROXY=http://127.0.0.1:7890
# or SOCKS5
export TWITTER_PROXY=socks5://127.0.0.1:1080
```

## Commands

### Read

```bash
twitter feed                                  # Home timeline (For You)
twitter feed -t following                     # Following timeline
twitter feed --max 50 --full-text             # Full post bodies
twitter feed --filter                         # Rank by engagement score

twitter bookmarks                             # Saved tweets
twitter bookmarks --max 30 --yaml             # Structured output

twitter search "keyword"                      # Search tweets
twitter search "AI" -t Latest --max 50        # Latest tab
twitter search "python" --from elonmusk --lang en --since 2026-01-01
twitter search --from bbc --exclude retweets --has links

twitter tweet 1234567890                      # Tweet detail + replies
twitter tweet https://x.com/user/status/123   # Accepts URLs
twitter show 2                                # Open tweet #2 from last list

twitter article 1234567890 --markdown         # Twitter Article as Markdown
twitter list 1539453138322673664              # List timeline

twitter user elonmusk                         # User profile
twitter user-posts elonmusk --max 20          # User's tweets
twitter likes elonmusk --max 30               # Own likes only (private since Jun 2024)
twitter followers elonmusk --max 50
twitter following elonmusk --max 50

twitter whoami                                # Current authenticated user
twitter status                                # Auth check

twitter trends                                # Trending topics (x.com Explore)
twitter trends --woeid 23424977 -n 20         # US trends (1 = worldwide)
twitter trend 2047489014127538677             # Tweets for a /i/trending/<id> cluster
twitter trend https://x.com/i/trending/...    # Accepts full URL

twitter dms                                   # List DM conversations
twitter dm <conversation_id> -n 50            # Read messages in a conversation
```

> **Trends note:** `twitter trends` reads the Explore/"What's happening" feed. The
> cluster ID in `/i/trending/<id>` URLs is served by an unstable internal op —
> if `twitter trend <id>` returns an internal error, fall back to
> `twitter search "<trend name>" --type Top`.

> **DMs note:** Read-only today (list inbox, read threads). Messages are
> returned newest-first in JSON/YAML output and rendered oldest-first
> (transcript order) in the rich table.

### Write

```bash
twitter post "Hello!"                         # Post tweet
twitter post "Hello!" --image photo.jpg       # With image (up to 4, JPEG/PNG/GIF/WebP)
twitter post "Gallery" -i a.png -i b.jpg      # Multiple images

twitter reply 1234567890 "Great tweet!"       # Reply
twitter reply 1234567890 "Nice!" -i pic.png   # Reply with image

twitter quote 1234567890 "Interesting"        # Quote-tweet
twitter quote 1234567890 "Look" -i chart.png  # Quote with image

twitter delete 1234567890                     # Delete own tweet
twitter like 1234567890                       # Like
twitter unlike 1234567890                     # Unlike
twitter retweet 1234567890                    # Retweet
twitter unretweet 1234567890                  # Unretweet
twitter bookmark 1234567890                   # Bookmark
twitter unbookmark 1234567890                 # Unbookmark
twitter follow elonmusk                       # Follow
twitter unfollow elonmusk                     # Unfollow
```

## Output Modes

| Mode | Flag | Use Case |
|------|------|----------|
| Rich table | *(default)* | Interactive terminal reading |
| Full text | `--full-text` | Complete post bodies in tables |
| YAML | `--yaml` | Structured output for scripts/agents |
| JSON | `--json` | Strict JSON parsing |
| Compact | `-c` / `--compact` | ~80% fewer tokens for LLMs |

Non-TTY stdout defaults to YAML. All structured output uses the envelope documented in [SCHEMA.md](./SCHEMA.md):

```yaml
ok: true
schema_version: "1"
data: [...]
```

## Configuration

Create `config.yaml` in your working directory or `~/.twitter-cli/`:

```yaml
fetch:
  count: 50                    # Default items per fetch

filter:
  mode: "topN"                 # "topN" | "score" | "all"
  topN: 20
  minScore: 50
  lang: []
  excludeRetweets: false
  weights:
    likes: 1.0
    retweets: 3.0
    replies: 2.0
    bookmarks: 5.0
    views_log: 0.5

rateLimit:
  requestDelay: 1.5            # Base delay between requests (jittered x0.7-1.5)
  maxRetries: 3
  retryBaseDelay: 5.0
  maxCount: 200
```

Filtering is opt-in — pass `--filter` to enable. Scoring formula:

```
score = likes_w * likes + retweets_w * retweets + replies_w * replies
      + bookmarks_w * bookmarks + views_log_w * log10(max(views, 1))
```

## NanoClaw Integration

twitter-cli is designed to work as a skill inside [NanoClaw](https://github.com/qwibitai/nanoclaw) — a container-based AI agent framework. There are two ways to integrate it:

### Option A: Container Skill (Simplest)

The container skill approach means twitter-cli runs inside the agent container. The agent calls it directly via bash. No IPC or host-side code needed.

**Step 1 — Install twitter-cli in the container Dockerfile**

Add to `container/Dockerfile`:

```dockerfile
RUN uv tool install twitter-cli
```

**Step 2 — Add credentials**

twitter-cli reads `TWITTER_AUTH_TOKEN` and `TWITTER_CT0` from environment variables. These are injected into the container at runtime by OneCLI or the native credential proxy (see NanoClaw docs).

Add to your `.env` or credential store:

```
TWITTER_AUTH_TOKEN=<your auth_token cookie>
TWITTER_CT0=<your ct0 cookie>
```

**Step 3 — Create the container skill**

Create `container/skills/twitter/SKILL.md`:

```markdown
---
name: twitter
description: Read and post on X (Twitter). Tweet, reply, search, read threads, check bookmarks, follow/unfollow.
---

# twitter — X (Twitter) CLI

Credentials are pre-configured via env vars.

## Commands
twitter feed -n 20                    # Timeline
twitter search "query" -n 20          # Search
twitter tweet <id>                    # Tweet detail
twitter post "text"                   # Post
twitter reply <id> "text"             # Reply
twitter like <id>                     # Like

## Safety Rules
- NEVER post, reply, like, retweet, or follow without explicit user approval
- Always confirm tweet content with the user before posting
- Read operations need no confirmation
```

That's it. The agent will see the skill and know how to use twitter-cli.

### Option B: Feature Skill with IPC (Advanced)

If you need host-side browser automation (e.g., Playwright-based posting for anti-detection), use the IPC pattern from the [x-integration skill](https://github.com/qwibitai/nanoclaw). This is more complex but avoids cookie-only auth limitations.

See the NanoClaw [CONTRIBUTING.md](https://github.com/qwibitai/nanoclaw/blob/main/CONTRIBUTING.md) for the full skill taxonomy.

### Which option to choose?

| | Container Skill | IPC Feature Skill |
|---|---|---|
| **Complexity** | Simple — CLI in container | Complex — host + container code |
| **Auth** | Cookie env vars | Browser session (Playwright) |
| **Anti-detection** | TLS fingerprinting (curl_cffi) | Full browser automation |
| **Write reliability** | Good (may get 226 on some accounts) | Best (real browser) |
| **Setup time** | 5 minutes | 30+ minutes |

For most users, **Option A** is sufficient.

## Adding Skills

twitter-cli supports a skill system for extending its capabilities inside AI agent frameworks. Skills are markdown files that teach AI agents how to perform specific workflows.

### Skill File Format

Skills follow the [Claude Code skills standard](https://code.claude.com/docs/en/skills):

```markdown
---
name: my-twitter-workflow
description: When to invoke this skill and what it does.
---

# Instructions

Step-by-step workflow here...
```

### Installing twitter-cli as a Skill

#### Skills CLI (Recommended)

```bash
npx skills add joelezra/twitter-cli
```

| Flag | Description |
|------|-------------|
| `-g` | Install globally (shared across projects) |
| `-a claude-code` | Target a specific agent |
| `-y` | Non-interactive mode |

#### Manual Install

```bash
mkdir -p .agents/skills
git clone https://github.com/joelezra/twitter-cli.git .agents/skills/twitter-cli
```

The [SKILL.md](./SKILL.md) file is automatically picked up by compatible AI agents.

### Creating Custom Workflows

You can create workflow skills that compose twitter-cli commands. Example — a daily digest skill:

```markdown
---
name: twitter-daily-digest
description: Generate a daily digest of top tweets from followed accounts.
---

# Daily Digest Workflow

1. Fetch following timeline:
   \`\`\`bash
   twitter feed -t following --max 50 --json
   \`\`\`
2. Filter by engagement (>100 likes)
3. Summarize the top 10 tweets
4. Post summary or save to file
```

### Agent Workflow Examples

```bash
# Post and verify
twitter post "My tweet" --json
# Output includes tweet URL

# Reply to someone's latest tweet
TWEET_ID=$(twitter user-posts user --max 1 --json | jq -r '.data[0].id')
twitter reply "$TWEET_ID" "Nice post!"

# Find most popular tweets
twitter user-posts user --max 20 --json | \
  jq '.data | sort_by(.metrics.likes) | reverse | .[:3]'

# Search + filter with jq
twitter search "AI safety" --max 20 --json | \
  jq '[.data[] | select(.metrics.likes > 100)]'
```

## Development

```bash
# Install dev dependencies
uv sync --extra dev

# Lint
uv run ruff check .

# Type check
uv run mypy twitter_cli

# Tests (excludes smoke tests)
uv run pytest -q

# Single test
uv run pytest tests/test_cli.py::test_feed_command -v

# Real API integration tests
uv run pytest -m smoke
```

### Project Structure

```
twitter_cli/
├── cli.py            # Click CLI entry point & commands
├── client.py         # Twitter GraphQL API client
├── auth.py           # Cookie extraction & authentication
├── graphql.py        # GraphQL query ID resolution
├── parser.py         # Tweet/User/Media parsing
├── models.py         # Dataclass models (Tweet, Author, etc.)
├── formatter.py      # Rich terminal table formatting
├── serialization.py  # YAML/JSON output
├── output.py         # Structured output helpers
├── config.py         # Config loading (YAML)
├── filter.py         # Tweet ranking & engagement scoring
├── search.py         # Advanced search query builder
├── cache.py          # Last-results caching
├── timeutil.py       # Timestamp parsing
├── constants.py      # Shared constants
└── exceptions.py     # Custom exception hierarchy
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `No Twitter cookies found` | Login to x.com in a supported browser, or set `TWITTER_AUTH_TOKEN` + `TWITTER_CT0` env vars. Run with `-v` for diagnostics. |
| `Cookie expired (401/403)` | Re-login to x.com and retry. |
| HTTP 226 (automated detection) | Use browser cookie extraction instead of env vars. |
| HTTP 404 (QueryId rotation) | Retry — auto-fallback is built in. Upgrade if persistent. |
| HTTP 429 (rate limited) | Wait 15+ minutes. Use `--max` to reduce request volume. |
| macOS Keychain locked (SSH) | `security unlock-keychain ~/Library/Keychains/login.keychain-db` |
| macOS Keychain (local) | Keychain Access -> search browser Safe Storage -> Access Control -> add Terminal -> Save |
| Windows pipe/subprocess empty | Use Git Bash + `"windowsEnableConpty": false` in terminal settings. |

### Best Practices (Avoiding Bans)

- Use a proxy (`TWITTER_PROXY`)
- Keep request volumes low (`--max 20`)
- Don't run too frequently (each startup hits x.com for anti-detection headers)
- Use browser cookie extraction for full fingerprint
- Avoid datacenter IPs — residential proxies are safer

## Error Codes

Structured errors returned in YAML/JSON output:

| Code | Meaning |
|------|---------|
| `not_authenticated` | Missing or invalid credentials |
| `rate_limited` | Too many requests — wait and retry |
| `not_found` | Tweet/user doesn't exist |
| `invalid_input` | Bad arguments |
| `api_error` | Upstream Twitter API error |

## Limitations

- **Images only** — no video/GIF upload (static JPEG/PNG/GIF/WebP supported)
- **No DMs** — direct messaging not supported
- **No notifications** — can't read notification timeline
- **No polls** — can't create polls
- **Single account** — one set of credentials at a time
- **Likes are private** — only your own likes visible (Twitter change, June 2024)

## License

[Apache-2.0](./LICENSE)
