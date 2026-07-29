# GitHub Star History Generator

A lightweight Python tool that dynamically samples star history from the GitHub REST API and generates a sleek, modern growth graph.

![google/skills Star History](file:///Users/rsamborski/projects/vibecoding/github-stars/google_skills_star_history.png)

## Key Features

- **Smart Adaptive Sampling**: Instead of fetching every stargazer page (which causes rate limits on large repos), the script dynamically calculates an optimal sampling interval (e.g. daily, weekly, or monthly) based on the repository's age.
- **Fast Parallel Fetching**: Uses `ThreadPoolExecutor` to fetch sampled pages concurrently in ~1-2 seconds with only ~15–40 total API requests.
- **Environment Token Authentication**: Checks `GITHUB_TOKEN`, `GH_TOKEN`, `GITHUB_CLASSIC_TOKEN`, or `PAT_TOKEN` environment variables. Uses standard `Bearer` authorization headers.
- **Modern Dark Theme Aesthetic**: Styled with a dark midnight background (`#0B0F19`), glowing cyan line (`#38BDF8`), translucent area fill, star badge, and formatted date/star tick labels.
- **PEP 723 Support**: Run directly via `uv run` with zero manual dependency setup.

## Usage

### 1. Set your GitHub Token (Optional but Recommended)

You can set `GITHUB_TOKEN` explicitly in your environment:

```bash
export GITHUB_TOKEN=$(gh auth token)
# or
export GITHUB_TOKEN="your_personal_access_token"
```

### 2. Run the Script

#### Option A: Using `uv` (Recommended - Auto-installs dependencies)

```bash
uv run star_history.py google/skills
```

#### Option B: Using standard Python

```bash
pip install requests matplotlib python-dateutil
python star_history.py google/skills
```

### Custom Output Path or Other Repositories

```bash
uv run star_history.py owner/repo -o custom_output.png
```
