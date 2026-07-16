from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass


API_BASE = "https://api.github.com"
API_VERSION = "2022-11-28"


@dataclass(frozen=True)
class GitHubStats:
    username: str
    public_repos: int
    followers: int
    following: int
    total_stars: int
    top_languages: tuple[str, ...]


def _request_json(url: str, token: str | None) -> object:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "github-terminal-profile",
        "X-GitHub-Api-Version": API_VERSION,
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"GitHub API request failed with HTTP {exc.code}: {details}"
        ) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not reach GitHub API: {exc.reason}") from exc


def fetch_github_stats(username: str, token: str | None = None) -> GitHubStats:
    safe_username = urllib.parse.quote(username, safe="")

    user_data = _request_json(f"{API_BASE}/users/{safe_username}", token)
    if not isinstance(user_data, dict):
        raise RuntimeError("Unexpected response from GitHub user endpoint.")

    repos: list[dict] = []
    page = 1

    while page <= 10:
        url = (
            f"{API_BASE}/users/{safe_username}/repos"
            f"?type=owner&sort=updated&per_page=100&page={page}"
        )
        page_data = _request_json(url, token)

        if not isinstance(page_data, list):
            raise RuntimeError("Unexpected response from GitHub repositories endpoint.")

        repos.extend(repo for repo in page_data if isinstance(repo, dict))

        if len(page_data) < 100:
            break

        page += 1

    total_stars = sum(int(repo.get("stargazers_count", 0) or 0) for repo in repos)

    language_counts: dict[str, int] = {}
    for repo in repos:
        if repo.get("fork"):
            continue

        language = repo.get("language")
        if isinstance(language, str) and language:
            language_counts[language] = language_counts.get(language, 0) + 1

    top_languages = tuple(
        language
        for language, _ in sorted(
            language_counts.items(),
            key=lambda item: (-item[1], item[0].lower()),
        )[:5]
    )

    return GitHubStats(
        username=username,
        public_repos=int(user_data.get("public_repos", 0) or 0),
        followers=int(user_data.get("followers", 0) or 0),
        following=int(user_data.get("following", 0) or 0),
        total_stars=total_stars,
        top_languages=top_languages,
    )
