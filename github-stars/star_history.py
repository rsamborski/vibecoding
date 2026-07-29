# /// script
# dependencies = [
#     "requests>=2.28.0",
#     "matplotlib>=3.6.0",
#     "python-dateutil>=2.8.2",
# ]
# ///

import os
import sys
import math
import subprocess
import argparse
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from dateutil import parser as date_parser
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

def get_github_token():
    """Retrieve GitHub token from environment variables."""
    for var in ["GITHUB_TOKEN", "GH_TOKEN", "GITHUB_CLASSIC_TOKEN", "PAT_TOKEN"]:
        token = os.environ.get(var)
        if token and token.strip():
            return token.strip()

    return None

def fetch_repo_info(owner, repo, headers):
    """Fetch repository metadata to get creation date and total star count."""
    url = f"https://api.github.com/repos/{owner}/{repo}"
    resp = requests.get(url, headers=headers)

    if resp.status_code == 401:
        print("Error: Invalid or expired GitHub token.", file=sys.stderr)
        sys.exit(1)
    elif resp.status_code == 404:
        print(f"Error: Repository '{owner}/{repo}' not found or private.", file=sys.stderr)
        sys.exit(1)
    elif resp.status_code == 403:
        print("Error: GitHub API rate limit exceeded. Provide a valid GITHUB_TOKEN.", file=sys.stderr)
        sys.exit(1)
    elif resp.status_code != 200:
        print(f"Error fetching repo info: HTTP {resp.status_code} - {resp.text}", file=sys.stderr)
        sys.exit(1)

    data = resp.json()
    return {
        "full_name": data.get("full_name", f"{owner}/{repo}"),
        "description": data.get("description", ""),
        "created_at": date_parser.parse(data["created_at"]),
        "stargazers_count": data.get("stargazers_count", 0),
        "html_url": data.get("html_url", f"https://github.com/{owner}/{repo}"),
    }

def fetch_page_sample(owner, repo, page, headers, retries=3):
    """Fetch a single page of stargazers to sample timestamps."""
    url = f"https://api.github.com/repos/{owner}/{repo}/stargazers?per_page=100&page={page}"
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code == 200:
                page_data = resp.json()
                if not page_data:
                    return page, []

                # Extract first and last item on the page for boundary timestamps
                samples = []
                if isinstance(page_data[0], dict) and "starred_at" in page_data[0]:
                    first_star_index = (page - 1) * 100 + 1
                    first_dt = date_parser.parse(page_data[0]["starred_at"])
                    samples.append((first_dt, first_star_index))

                if len(page_data) > 1 and isinstance(page_data[-1], dict) and "starred_at" in page_data[-1]:
                    last_star_index = (page - 1) * 100 + len(page_data)
                    last_dt = date_parser.parse(page_data[-1]["starred_at"])
                    samples.append((last_dt, last_star_index))

                return page, samples
            elif resp.status_code == 403:
                reset_time = resp.headers.get("X-RateLimit-Reset")
                print(f"\nWarning: Rate limit hit on page {page}. Retrying...", file=sys.stderr)
            elif resp.status_code == 422:
                return page, []
        except requests.RequestException as e:
            if attempt == retries - 1:
                print(f"\nFailed page {page}: {e}", file=sys.stderr)
    return page, []

def determine_sample_strategy(created_at, stargazers_count):
    """
    Calculate an optimal number of sample points and pages based on repo age and star count.
    """
    now = datetime.now(timezone.utc)
    age_days = max(1, (now - created_at).days)
    total_pages = math.ceil(stargazers_count / 100)
    if total_pages > 400:
        total_pages = 400 # GitHub REST API limit

    # Determine desired time interval and sample points
    if age_days <= 14:
        interval_desc = "daily"
        target_points = max(7, age_days)
    elif age_days <= 60:
        interval_desc = "every ~2-3 days"
        target_points = max(15, age_days // 3)
    elif age_days <= 180:
        interval_desc = "weekly"
        target_points = max(12, age_days // 7)
    elif age_days <= 365:
        interval_desc = "every ~10 days"
        target_points = max(20, age_days // 10)
    else:
        interval_desc = "monthly"
        target_points = max(24, age_days // 30)

    # Cap target points to reasonable bounds (between 15 and 40)
    target_points = min(40, max(15, target_points))

    # Determine pages to request
    if total_pages <= target_points:
        pages_to_fetch = list(range(1, total_pages + 1))
    else:
        # Linearly space pages between 1 and total_pages
        step = (total_pages - 1) / (target_points - 1)
        pages_to_fetch = sorted(list(dict.fromkeys([
            int(round(1 + i * step)) for i in range(target_points)
        ])))

    return pages_to_fetch, interval_desc, age_days

def fetch_sampled_star_history(owner, repo, created_at, stargazers_count, headers, max_workers=8):
    """Fetch star history by sampling pages across the repository timeline."""
    pages_to_fetch, interval_desc, age_days = determine_sample_strategy(created_at, stargazers_count)
    total_pages_to_fetch = len(pages_to_fetch)

    print(f"Repository age: {age_days} days | Total stars: {stargazers_count:,}")
    print(f"Sampling star growth ({total_pages_to_fetch} API requests, {interval_desc})...")

    sampled_points = []
    completed = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(fetch_page_sample, owner, repo, page, headers): page
            for page in pages_to_fetch
        }

        for future in as_completed(futures):
            page, page_samples = future.result()
            sampled_points.extend(page_samples)
            completed += 1
            percent = (completed / total_pages_to_fetch) * 100
            sys.stdout.write(f"\rProgress: [{completed}/{total_pages_to_fetch}] requests completed ({percent:.1f}%)")
            sys.stdout.flush()

    print("\nProcessing sampled star data...")

    # Sort data points by timestamp
    sampled_points.sort(key=lambda item: item[0])

    # Remove duplicate timestamps or star counts if any
    unique_points = []
    seen_times = set()
    for dt, count in sampled_points:
        if dt not in seen_times:
            unique_points.append((dt, count))
            seen_times.add(dt)

    return unique_points, interval_desc

def plot_star_history(repo_info, sampled_points, interval_desc, output_path, theme="whiteboard"):
    """
    Generate a star history graph following either whiteboard hand-drawn style or dark theme.
    By default, uses the Whiteboard / Visual Thinking sketch style (devrel-social-images).
    """
    import warnings
    import logging
    import matplotlib
    matplotlib.use('Agg')
    warnings.filterwarnings("ignore")
    logging.getLogger('matplotlib.font_manager').disabled = True

    created_at = repo_info["created_at"]
    total_stars = repo_info["stargazers_count"]
    full_name = repo_info["full_name"]
    now = datetime.now(timezone.utc)

    # Build timeline arrays starting from creation (0 stars) to present (total stars)
    dates = [created_at]
    counts = [0]

    for dt, count in sampled_points:
        dates.append(dt)
        counts.append(count)

    # Append current time and total stars
    if dates[-1] < now:
        dates.append(now)
        counts.append(total_stars)

    if theme == "whiteboard":
        # --- Whiteboard / Visual Thinking Style Setup ---
        bg_color = "#FFFFFF"        # Clean plain white whiteboard background
        text_dark = "#0F172A"       # Deep slate black marker text & strokes
        text_muted = "#64748B"      # Muted slate gray marker text
        accent_blue = "#2563EB"     # Vibrant marker blue for plot line
        grid_color = "#E2E8F0"      # Light hand-drawn grid lines
        star_amber = "#D97706"      # Marker yellow / gold text
        badge_bg = "#FEF3C7"        # Soft yellow marker badge background
        badge_edge = "#F59E0B"      # Marker yellow outline

        with plt.xkcd(scale=1.2, length=100, randomness=2):
            fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
            fig.patch.set_facecolor(bg_color)
            ax.set_facecolor(bg_color)

            # Plot smooth star growth line
            ax.plot(dates, counts, color=accent_blue, linewidth=3.2, zorder=4)

            # Fill area under curve with soft marker glow
            ax.fill_between(dates, counts, color=accent_blue, alpha=0.08, zorder=3)

            # Draw markers on sampled points
            if len(dates) <= 50:
                ax.scatter(dates[1:-1], counts[1:-1], color=accent_blue, s=20, alpha=0.7, zorder=5)

            # Highlight current endpoint
            ax.scatter([dates[-1]], [counts[-1]], color=accent_blue, s=70, zorder=6)

            # Title & Subtitle styling
            fig.text(0.08, 0.93, full_name, color=text_dark, fontsize=22, fontweight="bold", ha="left")
            subtitle_text = f"Star History • Created {created_at.strftime('%b %d, %Y')} • Sampled {interval_desc}"
            fig.text(0.08, 0.88, subtitle_text, color=text_muted, fontsize=11, ha="left")

            # Star Count Highlight Badge (Top Right Header)
            badge_box = dict(boxstyle="round,pad=0.5", facecolor=badge_bg, edgecolor=badge_edge, linewidth=1.5)
            fig.text(
                0.92, 0.91,
                f"*  {total_stars:,} stars",
                color=star_amber,
                fontsize=13,
                fontweight="bold",
                ha="right",
                va="center",
                bbox=badge_box,
            )

            # Formatting axes
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
            ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=4, maxticks=8))

            def count_formatter(x, pos):
                if x >= 1000:
                    return f"{x/1000:.1f}k"
                return f"{int(x)}"

            ax.yaxis.set_major_formatter(FuncFormatter(count_formatter))

            # Grid & Spines
            ax.grid(True, linestyle="--", linewidth=0.8, color=grid_color, alpha=0.7, zorder=1)

            for spine in ax.spines.values():
                spine.set_color(text_dark)
                spine.set_linewidth(1.5)

            ax.tick_params(axis="x", colors=text_dark, labelsize=10, pad=6)
            ax.tick_params(axis="y", colors=text_dark, labelsize=10, pad=6)

            ax.set_ylabel("GitHub Stars", color=text_dark, fontsize=11, labelpad=10)

            # Padding and layout
            plt.subplots_adjust(top=0.83, bottom=0.12, left=0.08, right=0.92)

            # Save output graph
            plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor="none", dpi=300)
            plt.close()
    else:
        # --- Modern Dark Theme Setup ---
        bg_color = "#0B0F19"        # Deep midnight background
        card_bg = "#111827"         # Plot area background
        accent_cyan = "#38BDF8"     # Electric sky cyan for main plot line
        grid_color = "#1F2937"      # Subtle grid lines
        text_white = "#F9FAFB"      # Crisp white headers
        text_muted = "#9CA3AF"      # Soft gray subtitles & axis labels
        star_gold = "#FBBF24"       # Warm gold for star badge

        fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(card_bg)

        # Plot smooth star growth line
        ax.plot(dates, counts, color=accent_cyan, linewidth=2.8, label="Stars", zorder=4)

        # Fill area under curve with soft glow
        ax.fill_between(dates, counts, color=accent_cyan, alpha=0.15, zorder=3)

        # Draw small markers on sampled points
        if len(dates) <= 50:
            ax.scatter(dates[1:-1], counts[1:-1], color=accent_cyan, s=18, alpha=0.7, zorder=5)

        # Highlight current endpoint
        ax.scatter([dates[-1]], [counts[-1]], color=accent_cyan, s=50, zorder=6)

        # Title & Subtitle styling
        fig.text(0.12, 0.92, full_name, color=text_white, fontsize=20, fontweight="bold", ha="left")
        subtitle_text = f"Star History • Created {created_at.strftime('%b %d, %Y')} • Sampled {interval_desc}"
        fig.text(0.12, 0.88, subtitle_text, color=text_muted, fontsize=11, ha="left")

        # Star Count Highlight Badge (Top Right)
        badge_box = dict(boxstyle="round,pad=0.5", facecolor="#1E293B", edgecolor="#334155", linewidth=1.2)
        ax.text(
            0.96, 0.92,
            f"*  {total_stars:,} stars",
            transform=ax.transAxes,
            color=star_gold,
            fontsize=13,
            fontweight="bold",
            ha="right",
            va="top",
            bbox=badge_box,
            zorder=7
        )

        # Formatting axes
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=4, maxticks=8))

        def count_formatter(x, pos):
            if x >= 1000:
                return f"{x/1000:.1f}k"
            return f"{int(x)}"

        ax.yaxis.set_major_formatter(FuncFormatter(count_formatter))

        # Grid & Spines
        ax.grid(True, linestyle="--", linewidth=0.7, color=grid_color, alpha=0.7, zorder=1)

        for spine in ax.spines.values():
            spine.set_color("#1F2937")
            spine.set_linewidth(1.0)

        ax.tick_params(axis="x", colors=text_muted, labelsize=10, pad=6)
        ax.tick_params(axis="y", colors=text_muted, labelsize=10, pad=6)

        ax.set_ylabel("GitHub Stars", color=text_muted, fontsize=11, labelpad=10)

        # Padding and tight layout
        plt.subplots_adjust(top=0.83, bottom=0.13, left=0.12, right=0.94)

        # Save output graph
        plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor="none", dpi=300)
        plt.close()

    print(f"\n✨ Graph saved successfully ({theme} theme) to: {output_path}")

def generate_demo_data(owner, repo):
    """Generate realistic synthetic star history for offline demo testing."""
    now = datetime.now(timezone.utc)
    created_at = now - timedelta(days=365)
    stargazers_count = 322
    repo_info = {
        "full_name": f"{owner}/{repo}",
        "description": "Demo repository for star history visualization",
        "created_at": created_at,
        "stargazers_count": stargazers_count,
        "html_url": f"https://github.com/{owner}/{repo}",
    }

    sampled_points = []
    for i in range(1, 25):
        dt = created_at + timedelta(days=i * 15)
        count = int((i / 24) ** 1.8 * stargazers_count)
        sampled_points.append((dt, count))

    return repo_info, sampled_points, "monthly demo"

def main():
    parser = argparse.ArgumentParser(description="Generate a sampled GitHub Star History graph in Whiteboard style.")
    parser.add_argument(
        "repo",
        nargs="?",
        default="google/skills",
        help="GitHub repository in 'owner/repo' format (default: google/skills)",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output file path for the graph image (default: <owner>_<repo>_star_history.png)",
    )
    parser.add_argument(
        "--theme",
        choices=["whiteboard", "dark"],
        default="whiteboard",
        help="Visual theme style (default: whiteboard)",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Generate graph using demo data without making GitHub API requests",
    )
    args = parser.parse_args()

    owner_repo = args.repo.strip("/")
    if "/" not in owner_repo:
        print("Error: Repository must be in 'owner/repo' format (e.g. google/skills)", file=sys.stderr)
        sys.exit(1)

    owner, repo = owner_repo.split("/", 1)
    output_path = args.output or f"{owner}_{repo}_star_history.png"

    if args.demo:
        print("Generating graph in demo mode (offline)...")
        repo_info, sampled_points, interval_desc = generate_demo_data(owner, repo)
    else:
        token = get_github_token()
        if token:
            print(f"Using GitHub authentication token.")
        else:
            print("Warning: No GitHub token found in GITHUB_TOKEN environment variable.", file=sys.stderr)
            print("Unauthenticated requests are rate-limited to 60 requests/hour.\n", file=sys.stderr)

        headers = {
            "Accept": "application/vnd.github.v3.star+json",
            "User-Agent": "star-history-script",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"

        # 1. Fetch Repo info
        repo_info = fetch_repo_info(owner, repo, headers)

        # 2. Fetch sampled star history points dynamically based on repo age & star count
        sampled_points, interval_desc = fetch_sampled_star_history(
            owner, repo, repo_info["created_at"], repo_info["stargazers_count"], headers
        )

    # 3. Render graph
    plot_star_history(repo_info, sampled_points, interval_desc, output_path, theme=args.theme)

if __name__ == "__main__":
    main()
