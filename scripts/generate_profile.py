from __future__ import annotations

import html
import os
from datetime import UTC, datetime
from pathlib import Path

from ascii import load_ascii_portrait
from github_stats import GitHubStats, fetch_github_stats


ROOT = Path(__file__).resolve().parents[1]
PORTRAIT_PATH = ROOT / "assets" / "portrait.txt"
OUTPUT_PATH = ROOT / "assets" / "profile.svg"


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def env(name: str, default: str) -> str:
    value = os.getenv(name, "").strip()
    return value or default


def build_readout(stats: GitHubStats) -> list[tuple[str, str]]:
    languages = ", ".join(stats.top_languages) or "Building in public"

    return [
        ("user", env("PROFILE_NAME", "Kshitij Chaudhary")),
        ("role", env("PROFILE_ROLE", "Full Stack Developer")),
        ("location", env("PROFILE_LOCATION", "Ontario, Canada")),
        ("mission", env("PROFILE_MISSION", "Building production-level software products")),
        ("current", env("PROFILE_CURRENT", "NepStack • Munmai • AI engineering")),
        ("stack", env("PROFILE_STACK", ".NET • Angular • TypeScript • Python")),
        ("languages", languages),
        ("repos", str(stats.public_repos)),
        ("followers", str(stats.followers)),
        ("stars", str(stats.total_stars)),
        ("status", env("PROFILE_STATUS", "Shipping, learning, improving")),
    ]


def render_svg(portrait: list[str], stats: GitHubStats) -> str:
    width = 1200
    height = 650
    line_height = 25
    portrait_x = 55
    portrait_y = 155
    details_x = 590
    details_y = 165

    portrait_nodes = []
    for index, line in enumerate(portrait):
        y = portrait_y + index * line_height
        portrait_nodes.append(
            f'<text x="{portrait_x}" y="{y}" class="portrait">{escape(line)}</text>'
        )

    detail_nodes = []
    for index, (key, value) in enumerate(build_readout(stats)):
        y = details_y + index * 38
        delay = 0.15 + index * 0.12
        detail_nodes.append(
            f'<g class="row" style="animation-delay:{delay:.2f}s">'
            f'<text x="{details_x}" y="{y}" class="key">{escape(key)}</text>'
            f'<text x="{details_x + 175}" y="{y}" class="value">{escape(value)}</text>'
            '</g>'
        )

    updated = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")

    return f"""<svg xmlns="http://www.w3.org/2000/svg"
     width="100%" height="100%" viewBox="0 0 {width} {height}"
     role="img" aria-labelledby="title description">
  <title id="title">{escape(env("PROFILE_NAME", "Xitol Mitra"))} terminal profile</title>
  <desc id="description">Animated terminal-style developer profile with GitHub statistics.</desc>

  <style>
    :root {{ color-scheme: light dark; }}
    .background {{ fill: #0d1117; }}
    .window {{ fill: #161b22; stroke: #30363d; stroke-width: 2; }}
    .toolbar {{ fill: #21262d; }}
    .title {{ fill: #c9d1d9; font: 600 22px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
    .prompt {{ fill: #7ee787; font: 600 21px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
    .portrait {{ fill: #a371f7; font: 18px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; white-space: pre; }}
    .key {{ fill: #7ee787; font: 600 19px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
    .value {{ fill: #c9d1d9; font: 19px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
    .footer {{ fill: #8b949e; font: 15px ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
    .row {{ opacity: 0; transform: translateY(5px); animation: reveal 0.35s ease forwards; }}
    .cursor {{ animation: blink 1s steps(1, end) infinite; }}
    @keyframes reveal {{ to {{ opacity: 1; transform: translateY(0); }} }}
    @keyframes blink {{ 0%, 48% {{ opacity: 1; }} 49%, 100% {{ opacity: 0; }} }}

    @media (prefers-color-scheme: light) {{
      .background {{ fill: #f6f8fa; }}
      .window {{ fill: #ffffff; stroke: #d0d7de; }}
      .toolbar {{ fill: #f6f8fa; }}
      .title, .value {{ fill: #24292f; }}
      .prompt, .key {{ fill: #1a7f37; }}
      .portrait {{ fill: #8250df; }}
      .footer {{ fill: #57606a; }}
    }}

    @media (prefers-reduced-motion: reduce) {{
      .row {{ opacity: 1; transform: none; animation: none; }}
      .cursor {{ animation: none; }}
    }}
  </style>

  <rect class="background" width="{width}" height="{height}" rx="24"/>
  <rect class="window" x="22" y="22" width="{width - 44}" height="{height - 44}" rx="18"/>
  <path class="toolbar" d="M40 22 H1160 A18 18 0 0 1 1178 40 V93 H22 V40 A18 18 0 0 1 40 22 Z"/>

  <circle cx="58" cy="58" r="9" fill="#ff5f56"/>
  <circle cx="88" cy="58" r="9" fill="#ffbd2e"/>
  <circle cx="118" cy="58" r="9" fill="#27c93f"/>

  <text x="600" y="66" text-anchor="middle" class="title">~/profile — terminal</text>
  <text x="55" y="125" class="prompt">$ neofetch --profile <tspan class="cursor">▋</tspan></text>

  {''.join(portrait_nodes)}
  {''.join(detail_nodes)}

  <line x1="550" y1="135" x2="550" y2="570" stroke="#30363d" stroke-width="2"/>
  <text x="55" y="605" class="footer">github.com/{escape(stats.username)}</text>
  <text x="1140" y="605" text-anchor="end" class="footer">updated {escape(updated)}</text>
</svg>
"""


def main() -> None:
    username = env("GITHUB_USERNAME", "")
    if not username:
        raise SystemExit(
            "GITHUB_USERNAME is required. "
            "Example: GITHUB_USERNAME=your-username python scripts/generate_profile.py"
        )

    token = os.getenv("GITHUB_TOKEN")
    stats = fetch_github_stats(username=username, token=token)
    portrait = load_ascii_portrait(PORTRAIT_PATH)
    svg = render_svg(portrait, stats)

    OUTPUT_PATH.write_text(svg, encoding="utf-8")
    print(f"Generated {OUTPUT_PATH.relative_to(ROOT)} for @{username}")


if __name__ == "__main__":
    main()
