# GitHub Star History Generator

A lightweight Python tool that dynamically samples star history from the GitHub REST API and generates a growth graph.

## Key Features

- **Whiteboard / Visual Thinking Style**: Designed in hand-drawn whiteboard marker sketch style following Developer Relations social image guidelines (clean white background, sketchy charcoal strokes, vibrant blue marker curve, and warm amber star badge).
- **Smart Adaptive Sampling**: Instead of fetching every stargazer page (which causes rate limits on large repos), the script dynamically calculates an optimal sampling interval (e.g. daily, weekly, or monthly) based on the repository's age.
- **Fast Parallel Fetching**: Uses `ThreadPoolExecutor` to fetch sampled pages concurrently in ~1-2 seconds with only ~15–40 total API requests.
- **Environment Token Authentication**: Checks `GITHUB_TOKEN`, `GH_TOKEN`, `GITHUB_CLASSIC_TOKEN`, or `PAT_TOKEN` environment variables.
- **Star Threshold Filtering**: Ignore inactive time before reaching a minimum star count (e.g. `--min-stars 10`) to clean up pre-launch timelines.
- **Themes & Demo Mode**: Supports `--theme whiteboard` (default) and `--theme dark`, as well as `--demo` mode for instant offline graph generation without API calls.
- **PEP 723 Support**: Run directly via `uv run` with zero manual dependency setup.

## Usage

### 1. Set your GitHub Token (Recommended)

Set `GITHUB_TOKEN` explicitly in your environment to avoid GitHub REST API rate limits:

```bash
export GITHUB_TOKEN=$(gh auth token)
# or
export GITHUB_TOKEN="your_personal_access_token"
```

### 2. Run the Script

#### Option A: Using `uv` (Recommended - Auto-installs dependencies)

```bash
# Whiteboard visual thinking style (Default)
uv run star_history.py owner/repo

# Dark theme style
uv run star_history.py owner/repo --theme dark

# Ignore timeline before reaching a star threshold (e.g., 10 stars)
uv run star_history.py owner/repo --min-stars 10

# Demo mode (Offline test data)
uv run star_history.py owner/repo --demo
```

#### Option B: Using standard Python

```bash
pip install requests matplotlib python-dateutil
python star_history.py owner/repo
```

### Custom Output Path

```bash
uv run star_history.py owner/repo -o custom_output.png
```
