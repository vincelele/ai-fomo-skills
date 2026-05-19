#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlparse
from urllib.request import Request, urlopen


USER_AGENT = "ai-fomo-sources/0.1 (+https://github.com/)"


@dataclass(slots=True)
class RawItem:
    source_name: str
    source_id: str
    source_type: str
    adapter: str
    title: str
    url: str
    published_at: str
    collected_at: str
    author: str
    item_id: str
    dedupe_key: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    status: str = "collected"
    content_kind: str = "normalized-text"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        item = collect(args)
        if args.dry_run:
            print(render_raw_item(item))
            return 0
        path = write_raw_item(Path(args.workspace), item)
        print(f"Wrote raw snapshot: {path}")
        print("Next step: use $ai-fomo to judge whether this source should be filed.")
        return 0
    except Exception as exc:
        print(f"Import failed: {exc}", file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="import_source.py",
        description="Import common AI FOMO sources into raw/inbox.",
    )
    parser.add_argument("--workspace", required=True, help="AI FOMO workspace path.")
    parser.add_argument("--dry-run", action="store_true", help="Print raw snapshot only.")
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--max-chars", type=int, default=20000)

    subparsers = parser.add_subparsers(dest="command", required=True)

    official = subparsers.add_parser("official-page", help="Import an official web page.")
    official.add_argument("--url", required=True)
    official.add_argument("--source-id")
    official.add_argument("--source-name")

    rss = subparsers.add_parser("rss", help="Import the latest items from an RSS/Atom feed.")
    rss.add_argument("--url", required=True)
    rss.add_argument("--source-id")
    rss.add_argument("--source-name")
    rss.add_argument("--limit", type=int, default=10)

    repo = subparsers.add_parser("github-repo", help="Import GitHub repo metadata and README.")
    repo.add_argument("--repo", required=True, help="owner/name")
    repo.add_argument("--source-id")
    repo.add_argument("--source-name")
    repo.add_argument("--github-token-env", default="GITHUB_TOKEN")

    trending = subparsers.add_parser("github-trending", help="Import GitHub trending snapshot.")
    trending.add_argument("--language", default="")
    trending.add_argument("--since", choices=["daily", "weekly", "monthly"], default="daily")
    trending.add_argument("--limit", type=int, default=25)
    trending.add_argument("--source-id")
    trending.add_argument("--source-name")

    x_user = subparsers.add_parser("x-user", help="Import recent X user posts with X API v2.")
    x_user.add_argument("--handle", required=True)
    x_user.add_argument("--source-id")
    x_user.add_argument("--source-name")
    x_user.add_argument("--bearer-token-env", default="X_BEARER_TOKEN")
    x_user.add_argument("--max-results", type=int, default=10)

    xyz = subparsers.add_parser("xiaoyuzhou-episode", help="Import Xiaoyuzhou episode metadata.")
    xyz.add_argument("--url", required=True)
    xyz.add_argument("--source-id")
    xyz.add_argument("--source-name")

    return parser


def collect(args: argparse.Namespace) -> RawItem:
    if args.command == "official-page":
        return collect_official_page(args)
    if args.command == "rss":
        return collect_rss(args)
    if args.command == "github-repo":
        return collect_github_repo(args)
    if args.command == "github-trending":
        return collect_github_trending(args)
    if args.command == "x-user":
        return collect_x_user(args)
    if args.command == "xiaoyuzhou-episode":
        return collect_xiaoyuzhou_episode(args)
    raise ValueError(f"Unsupported command: {args.command}")


def collect_official_page(args: argparse.Namespace) -> RawItem:
    html_text = fetch_text(args.url, timeout=args.timeout)
    metadata = HtmlMetadata()
    metadata.feed(html_text)
    text = extract_visible_text(html_text, max_chars=args.max_chars)
    title = metadata.title or host_label(args.url)
    source_id = args.source_id or slugify(host_label(args.url))
    source_name = args.source_name or host_label(args.url)
    collected_at = now_iso()
    content = "\n\n".join(
        part
        for part in [
            f"# {title}",
            metadata.description and f"Description: {metadata.description}",
            text,
        ]
        if part
    )
    return RawItem(
        source_name=source_name,
        source_id=source_id,
        source_type="official_page",
        adapter="official_page",
        title=title,
        url=args.url,
        published_at=collected_at[:10],
        collected_at=collected_at,
        author=source_name,
        item_id=slugify(title)[:80] or "official-page",
        dedupe_key=f"{source_id}:{args.url}",
        content=content,
        metadata={
            "importer": "ai-fomo-sources",
            "description": metadata.description,
            "canonical_url": metadata.canonical_url,
        },
    )


def collect_rss(args: argparse.Namespace) -> RawItem:
    xml_text = fetch_text(args.url, timeout=args.timeout)
    root = ET.fromstring(xml_text)
    feed_title = first_text(root, [".//channel/title", ".//{http://www.w3.org/2005/Atom}title"])
    entries = parse_feed_entries(root)[: max(1, args.limit)]
    source_id = args.source_id or slugify(feed_title or host_label(args.url))
    source_name = args.source_name or feed_title or host_label(args.url)
    collected_at = now_iso()
    lines = [f"# Feed Snapshot: {source_name}", ""]
    for idx, entry in enumerate(entries, start=1):
        lines.extend(
            [
                f"## {idx}. {entry['title']}",
                "",
                f"- URL: {entry['url']}",
                f"- Published: {entry['published_at']}",
                "",
                entry["summary"],
                "",
            ]
        )
    return RawItem(
        source_name=source_name,
        source_id=source_id,
        source_type="rss_feed",
        adapter="rss",
        title=f"Feed Snapshot: {source_name}",
        url=args.url,
        published_at=collected_at[:10],
        collected_at=collected_at,
        author=source_name,
        item_id=datetime.now(timezone.utc).strftime("feed-%Y%m%dT%H%M%S"),
        dedupe_key=f"{source_id}:{args.url}:{entries[0]['url'] if entries else collected_at}",
        content="\n".join(lines).strip(),
        metadata={"importer": "ai-fomo-sources", "entries": entries},
    )


def collect_github_repo(args: argparse.Namespace) -> RawItem:
    owner, name = parse_repo(args.repo)
    token = os.getenv(args.github_token_env, "").strip()
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    repo_payload = fetch_json(
        f"https://api.github.com/repos/{quote(owner)}/{quote(name)}",
        timeout=args.timeout,
        headers=headers,
    )
    readme_text = ""
    try:
        readme_payload = fetch_json(
            f"https://api.github.com/repos/{quote(owner)}/{quote(name)}/readme",
            timeout=args.timeout,
            headers={**headers, "Accept": "application/vnd.github.raw"},
            raw=True,
        )
        readme_text = str(readme_payload)[: args.max_chars]
    except Exception:
        readme_text = ""
    full_name = str(repo_payload.get("full_name") or f"{owner}/{name}")
    source_id = args.source_id or f"github-{slugify(full_name)}"
    source_name = args.source_name or full_name
    collected_at = now_iso()
    description = str(repo_payload.get("description") or "")
    content = "\n\n".join(
        [
            f"# GitHub Repo: {full_name}",
            description,
            "\n".join(
                [
                    f"- URL: {repo_payload.get('html_url', '')}",
                    f"- Stars: {repo_payload.get('stargazers_count', '')}",
                    f"- Forks: {repo_payload.get('forks_count', '')}",
                    f"- Language: {repo_payload.get('language', '')}",
                    f"- Topics: {', '.join(repo_payload.get('topics') or [])}",
                    f"- Created: {repo_payload.get('created_at', '')}",
                    f"- Updated: {repo_payload.get('updated_at', '')}",
                    f"- Pushed: {repo_payload.get('pushed_at', '')}",
                ]
            ),
            readme_text and f"## README\n\n{readme_text}",
        ]
    )
    return RawItem(
        source_name=source_name,
        source_id=source_id,
        source_type="github_repo",
        adapter="github_repo",
        title=f"GitHub Repo: {full_name}",
        url=str(repo_payload.get("html_url") or f"https://github.com/{full_name}"),
        published_at=str(repo_payload.get("created_at") or collected_at)[:10],
        collected_at=collected_at,
        author=owner,
        item_id=slugify(full_name),
        dedupe_key=f"github-repo:{full_name}:{repo_payload.get('pushed_at', '')}",
        content=content.strip(),
        metadata={
            "importer": "ai-fomo-sources",
            "github_repo": {
                "full_name": full_name,
                "html_url": repo_payload.get("html_url"),
                "description": repo_payload.get("description"),
                "stargazers_count": repo_payload.get("stargazers_count"),
                "forks_count": repo_payload.get("forks_count"),
                "open_issues_count": repo_payload.get("open_issues_count"),
                "language": repo_payload.get("language"),
                "topics": repo_payload.get("topics") or [],
                "license": (repo_payload.get("license") or {}).get("spdx_id")
                if isinstance(repo_payload.get("license"), dict)
                else None,
                "created_at": repo_payload.get("created_at"),
                "updated_at": repo_payload.get("updated_at"),
                "pushed_at": repo_payload.get("pushed_at"),
            },
        },
    )


def collect_github_trending(args: argparse.Namespace) -> RawItem:
    language_path = f"/{quote(args.language.strip())}" if args.language.strip() else ""
    url = f"https://github.com/trending{language_path}?since={args.since}"
    html_text = fetch_text(url, timeout=args.timeout)
    repos = parse_github_trending(html_text)[: max(1, args.limit)]
    source_id = args.source_id or f"github-trending-{slugify(args.language or 'all')}-{args.since}"
    source_name = args.source_name or f"GitHub Trending {args.language or 'All'} {args.since}"
    collected_at = now_iso()
    lines = [f"# {source_name}", "", f"- URL: {url}", f"- Collected: {collected_at}", ""]
    for idx, repo in enumerate(repos, start=1):
        lines.extend(
            [
                f"## {idx}. {repo['full_name']}",
                "",
                f"- URL: {repo['url']}",
                f"- Language: {repo['language']}",
                f"- Stars: {repo['stars']}",
                "",
                repo["description"],
                "",
            ]
        )
    return RawItem(
        source_name=source_name,
        source_id=source_id,
        source_type="github_trending",
        adapter="github_trending",
        title=source_name,
        url=url,
        published_at=collected_at[:10],
        collected_at=collected_at,
        author="GitHub",
        item_id=datetime.now(timezone.utc).strftime("trending-%Y%m%dT%H%M%S"),
        dedupe_key=f"{source_id}:{collected_at[:10]}",
        content="\n".join(lines).strip(),
        metadata={"importer": "ai-fomo-sources", "repos": repos},
    )


def collect_x_user(args: argparse.Namespace) -> RawItem:
    token = os.getenv(args.bearer_token_env, "").strip()
    if not token:
        raise ValueError(f"Missing X API bearer token env var: {args.bearer_token_env}")
    headers = {"Authorization": f"Bearer {token}"}
    user_payload = fetch_json(
        "https://api.x.com/2/users/by/username/"
        + quote(args.handle.lstrip("@"))
        + "?user.fields=name,username,description",
        timeout=args.timeout,
        headers=headers,
    )
    user = user_payload.get("data") or {}
    user_id = str(user.get("id") or "")
    if not user_id:
        raise ValueError(f"Could not resolve X handle: {args.handle}")
    query = urlencode(
        {
            "max_results": max(5, min(args.max_results, 100)),
            "tweet.fields": "created_at,public_metrics,conversation_id,referenced_tweets,text",
        }
    )
    timeline = fetch_json(
        f"https://api.x.com/2/users/{quote(user_id)}/tweets?{query}",
        timeout=args.timeout,
        headers=headers,
    )
    tweets = [tweet for tweet in timeline.get("data", []) if isinstance(tweet, dict)]
    source_id = args.source_id or f"x-{slugify(args.handle)}"
    source_name = args.source_name or f"X @{args.handle.lstrip('@')}"
    collected_at = now_iso()
    lines = [f"# Recent X Posts: @{args.handle.lstrip('@')}", ""]
    for idx, tweet in enumerate(tweets, start=1):
        tweet_id = tweet.get("id", "")
        lines.extend(
            [
                f"## {idx}. {tweet.get('created_at', '')}",
                "",
                f"- URL: https://x.com/{args.handle.lstrip('@')}/status/{tweet_id}",
                f"- Metrics: {json.dumps(tweet.get('public_metrics', {}), ensure_ascii=False)}",
                "",
                str(tweet.get("text", "")),
                "",
            ]
        )
    return RawItem(
        source_name=source_name,
        source_id=source_id,
        source_type="x_user_timeline",
        adapter="x_api_v2",
        title=f"Recent X Posts: @{args.handle.lstrip('@')}",
        url=f"https://x.com/{args.handle.lstrip('@')}",
        published_at=collected_at[:10],
        collected_at=collected_at,
        author=str(user.get("name") or args.handle),
        item_id=datetime.now(timezone.utc).strftime("x-%Y%m%dT%H%M%S"),
        dedupe_key=f"{source_id}:{tweets[0].get('id') if tweets else collected_at}",
        content="\n".join(lines).strip(),
        metadata={"importer": "ai-fomo-sources", "user": user, "tweets": tweets},
    )


def collect_xiaoyuzhou_episode(args: argparse.Namespace) -> RawItem:
    episode_id = extract_xiaoyuzhou_episode_id(args.url)
    html_text = fetch_text(args.url, timeout=args.timeout)
    metadata = HtmlMetadata()
    metadata.feed(html_text)
    next_data = parse_next_data(metadata.next_data)
    episode_record = find_episode_record(next_data, episode_id)
    title = (
        metadata.og_title
        or string_value(episode_record, "title", "name")
        or metadata.title
        or f"Xiaoyuzhou Episode {episode_id}"
    )
    podcast_title = (
        string_value(episode_record, "podcast_title", "podcastTitle", "podcast_name")
        or nested_string(episode_record, ("podcast", "title"))
        or "Xiaoyuzhou"
    )
    published_at = normalize_date(
        string_value(episode_record, "published_at", "publishedAt", "publishTime", "pubDate")
        or metadata.published_time
    )
    show_notes = clean_text(
        string_value(episode_record, "shownotes", "show_notes", "description", "detailContent", "content")
        or metadata.description
    )
    audio_url = (
        metadata.og_audio
        or nested_string(episode_record, ("audio", "url"))
        or nested_string(episode_record, ("enclosure", "url"))
        or string_value(episode_record, "audio_url", "audioUrl", "enclosureUrl")
    )
    source_id = args.source_id or "xiaoyuzhou-episodes"
    source_name = args.source_name or podcast_title
    collected_at = now_iso()
    display_published_at = published_at or collected_at[:10]
    content = "\n\n".join(
        [
            f"# {clean_text(title)}",
            f"- Podcast: {clean_text(podcast_title)}",
            f"- Episode URL: {args.url}",
            f"- Audio URL: {audio_url}",
            f"- Published: {display_published_at}",
            "## Show Notes",
            show_notes,
        ]
    )
    return RawItem(
        source_name=source_name,
        source_id=source_id,
        source_type="podcast_episode",
        adapter="xiaoyuzhou_episode",
        title=clean_text(title),
        url=args.url,
        published_at=display_published_at,
        collected_at=collected_at,
        author=clean_text(podcast_title),
        item_id=f"episode-{episode_id}",
        dedupe_key=f"xiaoyuzhou:{episode_id}",
        content=content.strip(),
        metadata={
            "importer": "ai-fomo-sources",
            "episode_id": episode_id,
            "podcast_title": podcast_title,
            "audio_url": audio_url,
            "notes": "Metadata and show notes only. Transcription requires a separate ASR workflow.",
        },
    )


def write_raw_item(workspace: Path, item: RawItem) -> Path:
    output_dir = workspace.expanduser().resolve() / "raw" / "inbox"
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{date_prefix(item)}-{slugify(item.source_id)}-{slugify(item.item_id)}.md"
    if not path.exists():
        path.write_text(render_raw_item(item), encoding="utf-8")
    return path


def render_raw_item(item: RawItem) -> str:
    frontmatter = {
        "source_name": item.source_name,
        "source_id": item.source_id,
        "source_type": item.source_type,
        "adapter": item.adapter,
        "title": item.title,
        "url": item.url,
        "published_at": item.published_at,
        "collected_at": item.collected_at,
        "author": item.author,
        "item_id": item.item_id,
        "dedupe_key": item.dedupe_key,
        "status": item.status,
        "content_kind": item.content_kind,
        "metadata": item.metadata,
    }
    lines = ["---"]
    for key, value in frontmatter.items():
        lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
    lines.extend(
        [
            "---",
            "",
            "## Content",
            "",
            item.content.rstrip(),
            "",
            "## Source Notes",
            "",
            str(item.metadata.get("notes") or "No additional source notes."),
            "",
            "## Metadata Dump",
            "",
            "```json",
            json.dumps(item.metadata, indent=2, ensure_ascii=False),
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def fetch_text(url: str, *, timeout: int, headers: dict[str, str] | None = None) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="replace")
    except HTTPError as exc:
        raise ValueError(f"HTTP {exc.code}: {url}") from exc
    except URLError as exc:
        raise ValueError(f"Request failed for {url}: {exc.reason}") from exc


def fetch_json(
    url: str,
    *,
    timeout: int,
    headers: dict[str, str] | None = None,
    raw: bool = False,
) -> Any:
    text = fetch_text(url, timeout=timeout, headers=headers)
    if raw:
        return text
    return json.loads(text)


class HtmlMetadata(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.description = ""
        self.canonical_url = ""
        self.og_title = ""
        self.og_audio = ""
        self.published_time = ""
        self.next_data = ""
        self._in_title = False
        self._in_next_data = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        mapping = {key.lower(): value or "" for key, value in attrs}
        if tag.lower() == "title":
            self._in_title = True
        if tag.lower() == "script" and mapping.get("id") == "__NEXT_DATA__":
            self._in_next_data = True
        if tag.lower() == "link" and mapping.get("rel") == "canonical":
            self.canonical_url = mapping.get("href", "")
        if tag.lower() == "meta":
            key = (mapping.get("property") or mapping.get("name") or "").lower()
            content = mapping.get("content", "").strip()
            if key == "description":
                self.description = content
            if key == "og:description" and not self.description:
                self.description = content
            if key == "og:title":
                self.og_title = content
            if key == "og:audio":
                self.og_audio = content
            if key in {"article:published_time", "og:release_date"}:
                self.published_time = content

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False
        if tag.lower() == "script":
            self._in_next_data = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data.strip()
        if self._in_next_data:
            self.next_data += data


class VisibleTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in {"script", "style", "noscript", "svg"}:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "noscript", "svg"} and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._skip_depth:
            text = clean_text(data)
            if text:
                self.parts.append(text)


def extract_visible_text(html_text: str, *, max_chars: int) -> str:
    parser = VisibleTextExtractor()
    parser.feed(html_text)
    text = "\n".join(parser.parts)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text[:max_chars]


def parse_feed_entries(root: ET.Element) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    rss_items = root.findall(".//item")
    atom_items = root.findall(".//{http://www.w3.org/2005/Atom}entry")
    for item in rss_items:
        entries.append(
            {
                "title": first_text(item, ["title"]) or "Untitled",
                "url": first_text(item, ["link"]) or "",
                "published_at": first_text(item, ["pubDate", "published"]) or "",
                "summary": clean_text(first_text(item, ["description", "summary"]) or ""),
            }
        )
    for item in atom_items:
        link = ""
        for link_item in item.findall("{http://www.w3.org/2005/Atom}link"):
            link = link_item.attrib.get("href", "")
            if link:
                break
        entries.append(
            {
                "title": first_text(item, ["{http://www.w3.org/2005/Atom}title"]) or "Untitled",
                "url": link,
                "published_at": first_text(
                    item,
                    [
                        "{http://www.w3.org/2005/Atom}published",
                        "{http://www.w3.org/2005/Atom}updated",
                    ],
                )
                or "",
                "summary": clean_text(
                    first_text(
                        item,
                        [
                            "{http://www.w3.org/2005/Atom}summary",
                            "{http://www.w3.org/2005/Atom}content",
                        ],
                    )
                    or ""
                ),
            }
        )
    return entries


def first_text(root: ET.Element, paths: list[str]) -> str:
    for path in paths:
        item = root.find(path)
        if item is not None and item.text and item.text.strip():
            return item.text.strip()
    return ""


def parse_github_trending(html_text: str) -> list[dict[str, str]]:
    articles = re.split(r"<article\b", html_text, flags=re.IGNORECASE)[1:]
    repos: list[dict[str, str]] = []
    for article in articles:
        href_match = re.search(r'href="(/[^/]+/[^"#?]+)"', article)
        if not href_match:
            continue
        full_name = href_match.group(1).strip("/").replace(" ", "")
        description_match = re.search(
            r'<p[^>]*class="[^"]*col-9[^"]*"[^>]*>(.*?)</p>',
            article,
            flags=re.DOTALL | re.IGNORECASE,
        ) or re.search(r'<p[^>]*>(.*?)</p>', article, flags=re.DOTALL | re.IGNORECASE)
        language_match = re.search(r'programmingLanguage"[^>]*>(.*?)</span>', article, flags=re.DOTALL)
        stars_match = re.search(r'<a[^>]+href="/[^/]+/[^/]+/stargazers"[^>]*>(.*?)</a>', article, flags=re.DOTALL)
        repos.append(
            {
                "full_name": clean_text(full_name),
                "url": f"https://github.com/{clean_text(full_name)}",
                "description": clean_text(strip_tags(description_match.group(1))) if description_match else "",
                "language": clean_text(strip_tags(language_match.group(1))) if language_match else "",
                "stars": clean_text(strip_tags(stars_match.group(1))) if stars_match else "",
            }
        )
    return repos


def extract_xiaoyuzhou_episode_id(url: str) -> str:
    parts = [part for part in urlparse(url).path.split("/") if part]
    if len(parts) >= 2 and parts[0] == "episode":
        return parts[1]
    raise ValueError(f"Unsupported Xiaoyuzhou episode URL: {url}")


def parse_next_data(raw: str) -> Any:
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def find_episode_record(data: Any, episode_id: str) -> dict[str, Any]:
    if isinstance(data, dict):
        if matches_episode(data, episode_id):
            return data
        for value in data.values():
            found = find_episode_record(value, episode_id)
            if found:
                return found
    if isinstance(data, list):
        for item in data:
            found = find_episode_record(item, episode_id)
            if found:
                return found
    return {}


def matches_episode(item: dict[str, Any], episode_id: str) -> bool:
    for key in ("episode_id", "episodeId", "eid", "id", "_id"):
        value = item.get(key)
        if isinstance(value, str) and value == episode_id:
            return True
    return False


def nested_string(item: dict[str, Any], path: tuple[str, ...]) -> str:
    current: Any = item
    for key in path:
        if not isinstance(current, dict):
            return ""
        current = current.get(key)
    return current.strip() if isinstance(current, str) else ""


def string_value(item: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def normalize_date(value: str) -> str:
    if not value:
        return ""
    match = re.search(r"\d{4}-\d{2}-\d{2}", value)
    return match.group(0) if match else value[:10]


def parse_repo(repo: str) -> tuple[str, str]:
    parts = [part for part in repo.strip().strip("/").split("/") if part]
    if len(parts) != 2:
        raise ValueError("--repo must use owner/name")
    return parts[0], parts[1]


def strip_tags(value: str) -> str:
    return re.sub(r"<[^>]+>", " ", value)


def clean_text(value: str) -> str:
    text = html.unescape(value or "")
    text = strip_tags(text)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n\s+", "\n", text)
    return text.strip()


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "item"


def host_label(url: str) -> str:
    host = urlparse(url).netloc or "web"
    return host.removeprefix("www.")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def date_prefix(item: RawItem) -> str:
    for candidate in (item.published_at, item.collected_at):
        if len(candidate) >= 10:
            return candidate[:10]
    return "unknown-date"


if __name__ == "__main__":
    raise SystemExit(main())
