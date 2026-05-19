#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, TypeVar
from urllib.parse import urlparse
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "http://127.0.0.1:23020"
DEFAULT_BRIDGE_REPO = "https://github.com/ultrazg/xyz.git"
DEFAULT_BRIDGE_RELATIVE_DIR = ".tools/xiaoyuzhou-bridge"
T = TypeVar("T")


class XiaoyuzhouAccountError(ValueError):
    """Raised when Xiaoyuzhou account import cannot complete."""


@dataclass(slots=True)
class AuthSession:
    uid: str
    nickname: str
    access_token: str
    refresh_token: str
    phone_number: str
    area_code: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AuthSession":
        return cls(
            uid=string_value(data, "uid"),
            nickname=string_value(data, "nickname") or "Unknown",
            access_token=string_value(data, "access_token", "accessToken"),
            refresh_token=string_value(data, "refresh_token", "refreshToken"),
            phone_number=string_value(data, "phone_number", "phoneNumber"),
            area_code=string_value(data, "area_code", "areaCode") or "+86",
        )


@dataclass(slots=True)
class Episode:
    episode_id: str
    title: str
    podcast_title: str
    episode_url: str
    audio_url: str
    published_at: str
    is_played: bool
    is_finished: bool
    is_favorited: bool
    source_tags: tuple[str, ...]


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
    metadata: dict[str, Any]


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return run(args)
    except Exception as exc:
        print(f"Xiaoyuzhou account command failed: {exc}", file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Login and batch-import Xiaoyuzhou subscribed episodes into AI FOMO raw snapshots."
    )
    parser.add_argument("--workspace", required=True, help="AI FOMO workspace path.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Local Xiaoyuzhou account API bridge URL.")
    parser.add_argument("--session-file", help="Defaults to <workspace>/.secrets/xiaoyuzhou_session.json.")
    parser.add_argument("--timeout", type=int, default=20)
    subparsers = parser.add_subparsers(dest="command", required=True)

    install_bridge = subparsers.add_parser("install-bridge", help="Clone and build the local Xiaoyuzhou bridge.")
    add_bridge_args(install_bridge)
    install_bridge.add_argument("--repo", default=DEFAULT_BRIDGE_REPO)
    install_bridge.add_argument("--ref", help="Optional git ref, branch, tag, or commit to checkout.")
    install_bridge.add_argument("--update", action="store_true", help="Run git pull when bridge dir already exists.")
    install_bridge.add_argument("--skip-build", action="store_true")
    install_bridge.add_argument("--start", action="store_true", help="Start the bridge after install.")
    install_bridge.add_argument("--dry-run", action="store_true")

    start_bridge = subparsers.add_parser("start-bridge", help="Start the local Xiaoyuzhou bridge.")
    add_bridge_args(start_bridge)
    start_bridge.add_argument("--foreground", action="store_true")
    start_bridge.add_argument("--start-timeout", type=int, default=15)

    stop_bridge = subparsers.add_parser("stop-bridge", help="Stop a bridge started by this script.")
    add_bridge_args(stop_bridge)

    status_bridge = subparsers.add_parser("bridge-status", help="Check whether the local Xiaoyuzhou bridge is listening.")
    add_bridge_args(status_bridge)

    send_code = subparsers.add_parser("send-code", help="Send SMS login code.")
    send_code.add_argument("--phone-number", required=True)
    send_code.add_argument("--area-code", default="+86")

    login_parser = subparsers.add_parser("login", help="Login with SMS verify code and save session.")
    login_parser.add_argument("--phone-number", required=True)
    login_parser.add_argument("--verify-code", required=True)
    login_parser.add_argument("--area-code", default="+86")

    subparsers.add_parser("session-status", help="Show saved session status without printing tokens.")
    subparsers.add_parser("refresh-session", help="Refresh and save account session.")

    inbox = subparsers.add_parser("import-inbox", help="Import subscribed inbox episodes.")
    inbox.add_argument("--limit", type=int, default=30)
    inbox.add_argument("--max-pages", type=int, default=3)
    inbox.add_argument("--with-comments", action="store_true", help="Also import comments for each imported episode.")
    inbox.add_argument("--comments-order", default="HOT")
    inbox.add_argument("--comments-max-pages", type=int, default=2)
    inbox.add_argument("--comments-include-replies", action="store_true")
    inbox.add_argument("--with-transcripts", action="store_true", help="Also transcribe each imported episode audio URL.")
    inbox.add_argument("--transcript-limit", type=int, help="Maximum number of imported episodes to transcribe.")
    add_transcription_args(inbox, include_dry_run=False)
    inbox.add_argument("--dry-run", action="store_true")

    comments = subparsers.add_parser("import-comments", help="Import primary comments for an episode.")
    comments.add_argument("--episode-id", required=True)
    comments.add_argument("--order", default="HOT")
    comments.add_argument("--max-pages", type=int, default=2)
    comments.add_argument("--include-replies", action="store_true")
    comments.add_argument("--dry-run", action="store_true")

    transcribe_audio = subparsers.add_parser("transcribe-audio", help="Transcribe an audio URL with DashScope Fun-ASR.")
    transcribe_audio.add_argument("--episode-id", required=True)
    transcribe_audio.add_argument("--audio-url", required=True)
    transcribe_audio.add_argument("--episode-url", default="")
    transcribe_audio.add_argument("--title", default="")
    transcribe_audio.add_argument("--podcast-title", default="Xiaoyuzhou")
    add_transcription_args(transcribe_audio, include_dry_run=True)

    transcribe_raw = subparsers.add_parser("transcribe-raw", help="Transcribe a Xiaoyuzhou raw snapshot with audio_url metadata.")
    transcribe_raw.add_argument("--raw-file", required=True)
    add_transcription_args(transcribe_raw, include_dry_run=True)

    return parser


def add_bridge_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--bridge-dir", help=f"Defaults to <workspace>/{DEFAULT_BRIDGE_RELATIVE_DIR}.")
    parser.add_argument("--port", type=int, help="Defaults to the port in --base-url.")


def run(args: argparse.Namespace) -> int:
    workspace = Path(args.workspace).expanduser().resolve()
    session_path = resolve_session_path(workspace, args.session_file)
    bridge_dir = resolve_bridge_dir(workspace, getattr(args, "bridge_dir", None))

    if args.command == "install-bridge":
        result = install_bridge(workspace=workspace, bridge_dir=bridge_dir, args=args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if args.start and not args.dry_run:
            start_result = start_bridge(workspace=workspace, bridge_dir=bridge_dir, args=args)
            print(json.dumps(start_result, ensure_ascii=False, indent=2))
        return 0

    if args.command == "start-bridge":
        print(json.dumps(start_bridge(workspace=workspace, bridge_dir=bridge_dir, args=args), ensure_ascii=False, indent=2))
        return 0

    if args.command == "stop-bridge":
        print(json.dumps(stop_bridge(bridge_dir=bridge_dir), ensure_ascii=False, indent=2))
        return 0

    if args.command == "bridge-status":
        print(json.dumps(bridge_status(bridge_dir=bridge_dir, base_url=args.base_url, port=args.port), ensure_ascii=False, indent=2))
        return 0

    if args.command == "send-code":
        send_code(
            args.base_url,
            phone_number=args.phone_number,
            area_code=args.area_code,
            timeout=args.timeout,
        )
        print(json.dumps({"ok": True, "message": "SMS code requested."}, ensure_ascii=False, indent=2))
        return 0

    if args.command == "login":
        auth = login(
            args.base_url,
            phone_number=args.phone_number,
            verify_code=args.verify_code,
            area_code=args.area_code,
            timeout=args.timeout,
        )
        save_session(session_path, auth)
        print(
            json.dumps(
                {
                    "ok": True,
                    "session_file": str(session_path),
                    "uid": auth.uid,
                    "nickname": auth.nickname,
                    "phone_number": mask_phone(auth.phone_number),
                    "has_access_token": bool(auth.access_token),
                    "has_refresh_token": bool(auth.refresh_token),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if args.command == "session-status":
        auth = load_session(session_path)
        print(
            json.dumps(
                {
                    "session_file": str(session_path),
                    "uid": auth.uid,
                    "nickname": auth.nickname,
                    "phone_number": mask_phone(auth.phone_number),
                    "area_code": auth.area_code,
                    "has_access_token": bool(auth.access_token),
                    "has_refresh_token": bool(auth.refresh_token),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if args.command == "refresh-session":
        auth = refresh_auth(args.base_url, auth=load_session(session_path), timeout=args.timeout)
        save_session(session_path, auth)
        print(json.dumps({"ok": True, "session_file": str(session_path)}, ensure_ascii=False, indent=2))
        return 0

    if args.command == "transcribe-audio":
        return transcribe_and_write(
            workspace=workspace,
            episode_id=args.episode_id,
            audio_url=args.audio_url,
            episode_url=args.episode_url,
            title=args.title or args.episode_id,
            podcast_title=args.podcast_title,
            args=args,
        )

    if args.command == "transcribe-raw":
        raw_context = parse_raw_snapshot(Path(args.raw_file).expanduser())
        return transcribe_and_write(
            workspace=workspace,
            episode_id=raw_context["episode_id"],
            audio_url=raw_context["audio_url"],
            episode_url=raw_context["episode_url"],
            title=raw_context["title"],
            podcast_title=raw_context["podcast_title"],
            args=args,
        )

    if args.command == "import-inbox":
        auth = load_session(session_path)
        if args.with_transcripts and not args.dry_run:
            require_api_key(args.api_key_env)
        items = run_with_session_refresh(
            args=args,
            auth=auth,
            session_path=session_path,
            operation=lambda current_auth: fetch_all_inbox(
                args.base_url,
                access_token=current_auth.access_token,
                max_pages=args.max_pages,
                timeout=args.timeout,
            ),
        )
        episodes = normalize_episodes(items, source_tag="inbox")[: max(0, args.limit)]
        raw_items = [episode_to_raw_item(episode) for episode in episodes]
        if args.dry_run:
            print(
                json.dumps(
                    {
                        "episode_count": len(raw_items),
                        "episodes": [item.metadata["episode"] for item in raw_items],
                        "planned_comments": args.with_comments,
                        "planned_transcripts": args.with_transcripts,
                        "comments_max_pages": args.comments_max_pages if args.with_comments else 0,
                        "transcript_count": count_transcript_targets(episodes, args.transcript_limit)
                        if args.with_transcripts
                        else 0,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 0
        summary = import_inbox_bundle(workspace=workspace, args=args, auth=auth, session_path=session_path, episodes=episodes)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        print("Next step: use $ai-fomo to judge the imported Xiaoyuzhou raw snapshots.")
        return 0

    if args.command == "import-comments":
        auth = load_session(session_path)
        comments_payload = run_with_session_refresh(
            args=args,
            auth=auth,
            session_path=session_path,
            operation=lambda current_auth: fetch_all_comments(
                args.base_url,
                access_token=current_auth.access_token,
                episode_id=args.episode_id,
                order=args.order,
                max_pages=args.max_pages,
                include_replies=args.include_replies,
                timeout=args.timeout,
            ),
        )
        item = comments_to_raw_item(args.episode_id, comments_payload)
        if args.dry_run:
            print(render_raw_item(item))
            return 0
        path = write_raw_item(workspace, item)
        print(json.dumps({"written": str(path), "comment_count": len(comments_payload["comments"])}, ensure_ascii=False, indent=2))
        print("Next step: use $ai-fomo to judge whether these comments add useful context.")
        return 0

    raise XiaoyuzhouAccountError(f"Unknown command: {args.command}")


def add_transcription_args(parser: argparse.ArgumentParser, *, include_dry_run: bool) -> None:
    parser.add_argument("--api-key-env", default="DASHSCOPE_API_KEY")
    parser.add_argument("--model", default="fun-asr")
    parser.add_argument("--language", default="zh")
    parser.add_argument("--poll-interval", type=int, default=10)
    parser.add_argument("--max-poll-attempts", type=int, default=90)
    parser.add_argument("--diarization-enabled", action="store_true")
    parser.add_argument("--speaker-count", type=int)
    if include_dry_run:
        parser.add_argument("--dry-run", action="store_true")


def install_bridge(*, workspace: Path, bridge_dir: Path, args: argparse.Namespace) -> dict[str, Any]:
    if args.dry_run:
        return {
            "would_install": True,
            "repo": args.repo,
            "ref": args.ref,
            "bridge_dir": str(bridge_dir),
            "would_build": not args.skip_build,
            "would_start": args.start,
        }

    require_command("git")
    if not bridge_dir.exists():
        bridge_dir.parent.mkdir(parents=True, exist_ok=True)
        run_command(["git", "clone", args.repo, str(bridge_dir)])
        cloned = True
    else:
        cloned = False
        if not (bridge_dir / ".git").exists():
            raise XiaoyuzhouAccountError(f"Bridge dir exists but is not a git checkout: {bridge_dir}")
        if args.update:
            run_command(["git", "-C", str(bridge_dir), "pull", "--ff-only"])

    if args.ref:
        run_command(["git", "-C", str(bridge_dir), "checkout", args.ref])

    binary_path = bridge_binary_path(bridge_dir)
    built = False
    if not args.skip_build:
        require_command("go")
        binary_path.parent.mkdir(parents=True, exist_ok=True)
        run_command(["go", "mod", "download"], cwd=bridge_dir)
        run_command(["go", "build", "-o", str(binary_path), "."], cwd=bridge_dir)
        built = True

    return {
        "installed": True,
        "cloned": cloned,
        "updated": bool(args.update and not cloned),
        "built": built,
        "repo": args.repo,
        "ref": current_git_ref(bridge_dir),
        "bridge_dir": str(bridge_dir),
        "binary": str(binary_path) if binary_path.exists() else None,
        "next_step": "start-bridge",
    }


def start_bridge(*, workspace: Path, bridge_dir: Path, args: argparse.Namespace) -> dict[str, Any]:
    host, port = bridge_host_port(args.base_url, args.port)
    if is_port_open(host, port, timeout_seconds=1):
        return {"running": True, "already_running": True, "base_url": f"http://{host}:{port}", "bridge_dir": str(bridge_dir)}
    if not bridge_dir.exists():
        raise XiaoyuzhouAccountError(f"Bridge dir not found. Run install-bridge first: {bridge_dir}")

    command, cwd = bridge_start_command(bridge_dir=bridge_dir, port=port)
    if bool(getattr(args, "foreground", False)):
        completed = subprocess.run(command, cwd=str(cwd), check=False)
        return {"running": completed.returncode == 0, "returncode": completed.returncode, "command": command}

    log_path = bridge_dir / "bridge.log"
    pid_path = bridge_pid_path(bridge_dir)
    log_file = log_path.open("ab")
    try:
        process = subprocess.Popen(
            command,
            cwd=str(cwd),
            stdout=log_file,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    finally:
        log_file.close()
    pid_path.write_text(str(process.pid) + "\n", encoding="utf-8")

    deadline = time.time() + max(1, int(getattr(args, "start_timeout", 15)))
    while time.time() < deadline:
        if process.poll() is not None:
            raise XiaoyuzhouAccountError(f"Bridge exited early with code {process.returncode}. See log: {log_path}")
        if is_port_open(host, port, timeout_seconds=1):
            return {
                "running": True,
                "pid": process.pid,
                "base_url": f"http://{host}:{port}",
                "bridge_dir": str(bridge_dir),
                "log": str(log_path),
            }
        time.sleep(1)

    raise XiaoyuzhouAccountError(f"Bridge did not start listening on {host}:{port}. See log: {log_path}")


def stop_bridge(*, bridge_dir: Path) -> dict[str, Any]:
    pid_path = bridge_pid_path(bridge_dir)
    if not pid_path.exists():
        return {"stopped": False, "reason": "pid file not found", "pid_file": str(pid_path)}
    raw_pid = pid_path.read_text(encoding="utf-8").strip()
    try:
        pid = int(raw_pid)
    except ValueError as exc:
        raise XiaoyuzhouAccountError(f"Invalid bridge pid file: {pid_path}") from exc
    try:
        if hasattr(os, "killpg"):
            os.killpg(pid, signal.SIGTERM)
        else:
            os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        pid_path.unlink(missing_ok=True)
        return {"stopped": False, "reason": "process not found", "pid": pid}
    pid_path.unlink(missing_ok=True)
    return {"stopped": True, "pid": pid}


def bridge_status(*, bridge_dir: Path, base_url: str, port: int | None) -> dict[str, Any]:
    host, resolved_port = bridge_host_port(base_url, port)
    return {
        "running": is_port_open(host, resolved_port, timeout_seconds=1),
        "host": host,
        "port": resolved_port,
        "base_url": f"http://{host}:{resolved_port}",
        "bridge_dir": str(bridge_dir),
        "pid_file": str(bridge_pid_path(bridge_dir)),
        "has_pid_file": bridge_pid_path(bridge_dir).exists(),
        "has_binary": bridge_binary_path(bridge_dir).exists(),
    }


def bridge_start_command(*, bridge_dir: Path, port: int) -> tuple[list[str], Path]:
    binary_path = bridge_binary_path(bridge_dir)
    if binary_path.exists():
        return [str(binary_path), "-p", str(port)], bridge_dir
    require_command("go")
    return ["go", "run", ".", "-p", str(port)], bridge_dir


def bridge_host_port(base_url: str, explicit_port: int | None) -> tuple[str, int]:
    parsed = urlparse(base_url)
    host = parsed.hostname or "127.0.0.1"
    port = explicit_port or parsed.port or 23020
    return host, port


def is_port_open(host: str, port: int, *, timeout_seconds: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout_seconds):
            return True
    except OSError:
        return False


def require_command(name: str) -> None:
    if shutil.which(name) is None:
        raise XiaoyuzhouAccountError(f"Required command not found: {name}")


def run_command(command: list[str], *, cwd: Path | None = None) -> None:
    try:
        subprocess.run(command, cwd=str(cwd) if cwd else None, check=True)
    except subprocess.CalledProcessError as exc:
        raise XiaoyuzhouAccountError(f"Command failed ({exc.returncode}): {' '.join(command)}") from exc


def current_git_ref(path: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--short", "HEAD"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except subprocess.CalledProcessError:
        return ""
    return completed.stdout.strip()


def bridge_binary_path(bridge_dir: Path) -> Path:
    name = "xyz.exe" if sys.platform == "win32" else "xyz"
    return bridge_dir / "bin" / name


def bridge_pid_path(bridge_dir: Path) -> Path:
    return bridge_dir / "bridge.pid"


def send_code(base_url: str, *, phone_number: str, area_code: str, timeout: int) -> None:
    post_json(
        base_url,
        "/sendCode",
        {"mobilePhoneNumber": phone_number, "areaCode": area_code},
        timeout=timeout,
    )


def login(base_url: str, *, phone_number: str, verify_code: str, area_code: str, timeout: int) -> AuthSession:
    payload = post_json(
        base_url,
        "/login",
        {"mobilePhoneNumber": phone_number, "verifyCode": verify_code, "areaCode": area_code},
        timeout=timeout,
    )
    wrapper = as_mapping(payload.get("data"))
    user = as_mapping(wrapper.get("data"))
    access_token = string_value(wrapper, "x-jike-access-token", "accessToken")
    refresh_token = string_value(wrapper, "x-jike-refresh-token", "refreshToken")
    uid = string_value(user, "uid")
    if not uid or not access_token or not refresh_token:
        raise XiaoyuzhouAccountError("Login response did not include uid/access token/refresh token.")
    return AuthSession(
        uid=uid,
        nickname=string_value(user, "nickname") or "Unknown",
        access_token=access_token,
        refresh_token=refresh_token,
        phone_number=phone_number,
        area_code=area_code,
    )


def refresh_auth(base_url: str, *, auth: AuthSession, timeout: int) -> AuthSession:
    payload = post_json(
        base_url,
        "/refresh_token",
        {
            "x-jike-access-token": auth.access_token,
            "x-jike-refresh-token": auth.refresh_token,
        },
        access_token=auth.access_token,
        extra_headers={"x-jike-refresh-token": auth.refresh_token},
        timeout=timeout,
    )
    data = as_mapping(payload.get("data"))
    access_token = string_value(data, "x-jike-access-token", "accessToken")
    refresh_token = string_value(data, "x-jike-refresh-token", "refreshToken")
    if not access_token or not refresh_token:
        raise XiaoyuzhouAccountError("Refresh response did not include updated tokens.")
    return AuthSession(
        uid=auth.uid,
        nickname=auth.nickname,
        access_token=access_token,
        refresh_token=refresh_token,
        phone_number=auth.phone_number,
        area_code=auth.area_code,
    )


def fetch_inbox_page(
    base_url: str,
    *,
    access_token: str,
    load_more_key: object | None,
    timeout: int,
) -> tuple[list[dict[str, Any]], object | None]:
    payload: dict[str, Any] = {}
    if load_more_key is not None:
        payload["loadMoreKey"] = load_more_key
    response = post_json(base_url, "/inbox_list", payload, access_token=access_token, timeout=timeout)
    data = as_mapping(response.get("data"))
    return list_of_mappings(data.get("data")), data.get("loadMoreKey")


def fetch_all_inbox(base_url: str, *, access_token: str, max_pages: int, timeout: int) -> list[dict[str, Any]]:
    all_items: list[dict[str, Any]] = []
    load_more_key: object | None = None
    for _ in range(max(1, max_pages)):
        items, load_more_key = fetch_inbox_page(
            base_url,
            access_token=access_token,
            load_more_key=load_more_key,
            timeout=timeout,
        )
        all_items.extend(items)
        if load_more_key is None:
            break
    return all_items


def fetch_comment_primary(
    base_url: str,
    *,
    access_token: str,
    episode_id: str,
    order: str,
    load_more_key: object | None,
    timeout: int,
) -> tuple[list[dict[str, Any]], object | None, int | None]:
    payload: dict[str, Any] = {"eid": episode_id, "id": episode_id, "order": order}
    if load_more_key is not None:
        payload["loadMoreKey"] = load_more_key
    response = post_json(base_url, "/comment_primary", payload, access_token=access_token, timeout=timeout)
    data = as_mapping(response.get("data"))
    total_count = data.get("totalCount")
    return (
        list_of_mappings(data.get("data")),
        data.get("loadMoreKey"),
        total_count if isinstance(total_count, int) else None,
    )


def fetch_comment_thread(
    base_url: str,
    *,
    access_token: str,
    primary_comment_id: str,
    order: str,
    timeout: int,
) -> tuple[list[dict[str, Any]], int | None]:
    response = post_json(
        base_url,
        "/comment_thread",
        {"primaryCommentId": primary_comment_id, "order": order},
        access_token=access_token,
        timeout=timeout,
    )
    data = as_mapping(response.get("data"))
    total_count = data.get("totalCount")
    return list_of_mappings(data.get("data")), total_count if isinstance(total_count, int) else None


def fetch_all_comments(
    base_url: str,
    *,
    access_token: str,
    episode_id: str,
    order: str,
    max_pages: int,
    include_replies: bool,
    timeout: int,
) -> dict[str, Any]:
    comments: list[dict[str, Any]] = []
    load_more_key: object | None = None
    total_count: int | None = None
    for _ in range(max(1, max_pages)):
        items, load_more_key, page_total_count = fetch_comment_primary(
            base_url,
            access_token=access_token,
            episode_id=episode_id,
            order=order,
            load_more_key=load_more_key,
            timeout=timeout,
        )
        comments.extend(items)
        total_count = page_total_count if page_total_count is not None else total_count
        if load_more_key is None:
            break

    replies_by_comment_id: dict[str, list[dict[str, Any]]] = {}
    if include_replies:
        for comment in comments:
            comment_id = string_value(comment, "id", "cid", "commentId")
            if not comment_id:
                continue
            replies, _ = fetch_comment_thread(
                base_url,
                access_token=access_token,
                primary_comment_id=comment_id,
                order="SMART",
                timeout=timeout,
            )
            if replies:
                replies_by_comment_id[comment_id] = replies

    return {
        "episode_id": episode_id,
        "order": order,
        "total_count": total_count,
        "comments": comments,
        "replies_by_comment_id": replies_by_comment_id,
    }


def normalize_episodes(records: list[dict[str, Any]], *, source_tag: str) -> list[Episode]:
    episodes: list[Episode] = []
    seen: set[str] = set()
    for record in records:
        try:
            episode = normalize_episode(record, source_tag=source_tag)
        except XiaoyuzhouAccountError:
            continue
        if episode.episode_id in seen:
            continue
        seen.add(episode.episode_id)
        episodes.append(episode)
    episodes.sort(key=lambda item: item.published_at, reverse=True)
    return episodes


def normalize_episode(record: dict[str, Any], *, source_tag: str) -> Episode:
    episode = as_mapping(record.get("episode")) if isinstance(record.get("episode"), dict) else record
    episode_id = string_value(episode, "eid", "id", "episodeId")
    if not episode_id:
        raise XiaoyuzhouAccountError("Episode payload is missing eid.")
    podcast_title = (
        string_value(as_mapping(episode.get("podcast")), "title", "name")
        or string_value(episode, "author")
        or "Xiaoyuzhou"
    )
    audio_url = (
        nested_string(episode, ("media", "source", "url"))
        or nested_string(episode, ("enclosure", "url"))
        or nested_string(episode, ("media", "url"))
    )
    return Episode(
        episode_id=episode_id,
        title=string_value(episode, "title", "name") or episode_id,
        podcast_title=podcast_title,
        episode_url=f"https://www.xiaoyuzhoufm.com/episode/{episode_id}",
        audio_url=audio_url,
        published_at=normalize_date(string_value(episode, "pubDate", "publishedAt", "published_at")),
        is_played=bool_value(episode.get("isPlayed")),
        is_finished=bool_value(episode.get("isFinished")),
        is_favorited=bool_value(episode.get("isFavorited")),
        source_tags=(source_tag,),
    )


def episode_to_raw_item(episode: Episode) -> RawItem:
    collected_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    published_at = episode.published_at or collected_at[:10]
    content = "\n\n".join(
        [
            f"# {episode.title}",
            f"- Podcast: {episode.podcast_title}",
            f"- Episode URL: {episode.episode_url}",
            f"- Audio URL: {episode.audio_url}",
            f"- Published: {published_at}",
            f"- Played: {episode.is_played}",
            f"- Finished: {episode.is_finished}",
            f"- Favorited: {episode.is_favorited}",
            "",
            "Imported from the user's Xiaoyuzhou subscribed inbox. Transcript generation requires a separate ASR workflow.",
        ]
    )
    return RawItem(
        source_name="Xiaoyuzhou Subscribed Inbox",
        source_id="xiaoyuzhou-inbox",
        source_type="podcast_episode",
        adapter="xiaoyuzhou_account_inbox",
        title=episode.title,
        url=episode.episode_url,
        published_at=published_at,
        collected_at=collected_at,
        author=episode.podcast_title,
        item_id=f"episode-{episode.episode_id}",
        dedupe_key=f"xiaoyuzhou-inbox:{episode.episode_id}",
        content=content.strip(),
        metadata={
            "importer": "ai-fomo-sources",
            "notes": "Imported from authenticated Xiaoyuzhou inbox. No transcript included.",
            "episode": {
                "episode_id": episode.episode_id,
                "title": episode.title,
                "podcast_title": episode.podcast_title,
                "episode_url": episode.episode_url,
                "audio_url": episode.audio_url,
                "published_at": published_at,
                "is_played": episode.is_played,
                "is_finished": episode.is_finished,
                "is_favorited": episode.is_favorited,
                "source_tags": list(episode.source_tags),
            },
        },
    )


def comments_to_raw_item(episode_id: str, payload: dict[str, Any]) -> RawItem:
    collected_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    comments = payload.get("comments") if isinstance(payload.get("comments"), list) else []
    replies_by_comment_id = (
        payload.get("replies_by_comment_id")
        if isinstance(payload.get("replies_by_comment_id"), dict)
        else {}
    )
    lines = [
        f"# Xiaoyuzhou Comments: {episode_id}",
        "",
        f"- Episode URL: https://www.xiaoyuzhoufm.com/episode/{episode_id}",
        f"- Order: {payload.get('order')}",
        f"- Total count reported: {payload.get('total_count')}",
        f"- Imported comments: {len(comments)}",
        "",
    ]
    for idx, comment in enumerate(comments, start=1):
        comment_id = string_value(comment, "id", "cid", "commentId") or f"comment-{idx}"
        text = comment_text(comment)
        user = comment_user_name(comment)
        lines.extend(
            [
                f"## {idx}. {user}",
                "",
                f"- Comment ID: {comment_id}",
                "",
                text or json.dumps(comment, ensure_ascii=False),
                "",
            ]
        )
        replies = replies_by_comment_id.get(comment_id)
        if isinstance(replies, list) and replies:
            lines.append("### Replies")
            lines.append("")
            for reply in replies:
                lines.append(f"- {comment_user_name(reply)}: {comment_text(reply) or json.dumps(reply, ensure_ascii=False)}")
            lines.append("")

    return RawItem(
        source_name="Xiaoyuzhou Comments",
        source_id="xiaoyuzhou-comments",
        source_type="podcast_comments",
        adapter="xiaoyuzhou_account_comments",
        title=f"Xiaoyuzhou Comments: {episode_id}",
        url=f"https://www.xiaoyuzhoufm.com/episode/{episode_id}",
        published_at=collected_at[:10],
        collected_at=collected_at,
        author="Xiaoyuzhou",
        item_id=f"comments-{episode_id}",
        dedupe_key=f"xiaoyuzhou-comments:{episode_id}:{payload.get('order')}",
        content="\n".join(lines).strip(),
        metadata={
            "importer": "ai-fomo-sources",
            "notes": "Imported from authenticated Xiaoyuzhou comments.",
            "episode_id": episode_id,
            "comment_count": len(comments),
            "total_count": payload.get("total_count"),
            "order": payload.get("order"),
            "include_replies": bool(replies_by_comment_id),
            "comments": comments,
            "replies_by_comment_id": replies_by_comment_id,
        },
    )


def import_inbox_bundle(
    *,
    workspace: Path,
    args: argparse.Namespace,
    auth: AuthSession,
    session_path: Path,
    episodes: list[Episode],
) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "episode_count": len(episodes),
        "episode_files": [],
        "comment_files": [],
        "transcript_files": [],
        "failures": [],
    }

    for episode in episodes:
        path = write_raw_item(workspace, episode_to_raw_item(episode))
        summary["episode_files"].append(str(path))

    if args.with_comments:
        for episode in episodes:
            try:
                comments_payload = run_with_session_refresh(
                    args=args,
                    auth=load_session(session_path) if session_path.exists() else auth,
                    session_path=session_path,
                    operation=lambda current_auth, current_episode=episode: fetch_all_comments(
                        args.base_url,
                        access_token=current_auth.access_token,
                        episode_id=current_episode.episode_id,
                        order=args.comments_order,
                        max_pages=args.comments_max_pages,
                        include_replies=args.comments_include_replies,
                        timeout=args.timeout,
                    ),
                )
                item = comments_to_raw_item(episode.episode_id, comments_payload)
                path = write_raw_item(workspace, item)
                summary["comment_files"].append(
                    {
                        "episode_id": episode.episode_id,
                        "file": str(path),
                        "comment_count": len(comments_payload["comments"]),
                    }
                )
            except Exception as exc:
                summary["failures"].append(
                    {"stage": "comments", "episode_id": episode.episode_id, "error": str(exc)}
                )

    if args.with_transcripts:
        api_key = require_api_key(args.api_key_env)
        for episode in transcript_targets(episodes, args.transcript_limit):
            if not episode.audio_url:
                summary["failures"].append(
                    {"stage": "transcript", "episode_id": episode.episode_id, "error": "Missing audio URL."}
                )
                continue
            try:
                item = transcribe_audio_to_raw_item(
                    episode_id=episode.episode_id,
                    audio_url=episode.audio_url,
                    episode_url=episode.episode_url,
                    title=episode.title,
                    podcast_title=episode.podcast_title,
                    args=args,
                    api_key=api_key,
                )
                path = write_raw_item(workspace, item)
                summary["transcript_files"].append({"episode_id": episode.episode_id, "file": str(path)})
            except Exception as exc:
                summary["failures"].append(
                    {"stage": "transcript", "episode_id": episode.episode_id, "error": str(exc)}
                )

    return summary


def transcript_targets(episodes: list[Episode], limit: int | None) -> list[Episode]:
    targets = [episode for episode in episodes if episode.audio_url]
    if limit is None:
        return targets
    return targets[: max(0, limit)]


def count_transcript_targets(episodes: list[Episode], limit: int | None) -> int:
    return len(transcript_targets(episodes, limit))


def require_api_key(env_var: str) -> str:
    api_key = os.getenv(env_var, "").strip()
    if not api_key:
        raise XiaoyuzhouAccountError(f"Missing DashScope API key env var: {env_var}")
    return api_key


def transcribe_and_write(
    *,
    workspace: Path,
    episode_id: str,
    audio_url: str,
    episode_url: str,
    title: str,
    podcast_title: str,
    args: argparse.Namespace,
) -> int:
    if not audio_url:
        raise XiaoyuzhouAccountError("Missing audio URL for transcription.")
    if args.dry_run:
        print(
            json.dumps(
                {
                    "episode_id": episode_id,
                    "audio_url": audio_url,
                    "api_key_env": args.api_key_env,
                    "model": args.model,
                    "language": args.language,
                    "would_submit": True,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    api_key = require_api_key(args.api_key_env)
    item = transcribe_audio_to_raw_item(
        episode_id=episode_id,
        audio_url=audio_url,
        episode_url=episode_url,
        title=title,
        podcast_title=podcast_title,
        args=args,
        api_key=api_key,
    )
    path = write_raw_item(workspace, item)
    print(json.dumps({"written": str(path), "task_id": item.metadata["dashscope_task_id"]}, ensure_ascii=False, indent=2))
    print("Next step: use $ai-fomo to judge the transcript raw snapshot.")
    return 0


def transcribe_audio_to_raw_item(
    *,
    episode_id: str,
    audio_url: str,
    episode_url: str,
    title: str,
    podcast_title: str,
    args: argparse.Namespace,
    api_key: str,
) -> RawItem:
    task = dashscope_submit_transcription(
        api_key=api_key,
        audio_url=audio_url,
        model=args.model,
        language=args.language,
        diarization_enabled=args.diarization_enabled,
        speaker_count=args.speaker_count,
        timeout=args.timeout,
    )
    task = dashscope_wait_for_task(
        api_key=api_key,
        task_id=task["task_id"],
        poll_interval=args.poll_interval,
        max_poll_attempts=args.max_poll_attempts,
        timeout=args.timeout,
    )
    transcription_url = task.get("transcription_url")
    if not isinstance(transcription_url, str) or not transcription_url:
        raise XiaoyuzhouAccountError("DashScope task succeeded without transcription_url.")
    transcript = dashscope_download_transcript(transcription_url=transcription_url, timeout=args.timeout)
    item = transcript_to_raw_item(
        episode_id=episode_id,
        audio_url=audio_url,
        episode_url=episode_url,
        title=title,
        podcast_title=podcast_title,
        task_id=str(task["task_id"]),
        transcript_text=transcript["text"],
        transcription_model=args.model,
    )
    return item


def transcript_to_raw_item(
    *,
    episode_id: str,
    audio_url: str,
    episode_url: str,
    title: str,
    podcast_title: str,
    task_id: str,
    transcript_text: str,
    transcription_model: str,
) -> RawItem:
    collected_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return RawItem(
        source_name="Xiaoyuzhou Transcript",
        source_id="xiaoyuzhou-transcripts",
        source_type="podcast_transcript",
        adapter="xiaoyuzhou_dashscope_transcript",
        title=f"Transcript: {title}",
        url=episode_url or f"https://www.xiaoyuzhoufm.com/episode/{episode_id}",
        published_at=collected_at[:10],
        collected_at=collected_at,
        author=podcast_title or "Xiaoyuzhou",
        item_id=f"transcript-{episode_id}",
        dedupe_key=f"xiaoyuzhou-transcript:{episode_id}:{task_id}",
        content=transcript_text.strip(),
        metadata={
            "importer": "ai-fomo-sources",
            "notes": "Transcribed from Xiaoyuzhou audio URL via DashScope async Fun-ASR.",
            "episode_id": episode_id,
            "episode_url": episode_url,
            "audio_url": audio_url,
            "podcast_title": podcast_title,
            "transcript_status": "succeeded",
            "transcription_provider": "fun_asr_dashscope",
            "transcription_model": transcription_model,
            "dashscope_task_id": task_id,
        },
    )


def dashscope_submit_transcription(
    *,
    api_key: str,
    audio_url: str,
    model: str,
    language: str,
    diarization_enabled: bool,
    speaker_count: int | None,
    timeout: int,
) -> dict[str, Any]:
    parameters: dict[str, Any] = {"channel_id": [0]}
    if language:
        parameters["language_hints"] = [language]
    if diarization_enabled:
        parameters["diarization_enabled"] = True
        if speaker_count is not None:
            parameters["speaker_count"] = speaker_count
    response = request_json(
        method="POST",
        url="https://dashscope.aliyuncs.com/api/v1/services/audio/asr/transcription",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable",
        },
        payload={"model": model, "input": {"file_urls": [audio_url]}, "parameters": parameters},
        timeout=timeout,
    )
    return parse_dashscope_task(response)


def dashscope_wait_for_task(
    *,
    api_key: str,
    task_id: str,
    poll_interval: int,
    max_poll_attempts: int,
    timeout: int,
) -> dict[str, Any]:
    last_task: dict[str, Any] | None = None
    for _ in range(max(1, max_poll_attempts)):
        task = dashscope_fetch_task(api_key=api_key, task_id=task_id, timeout=timeout)
        last_task = task
        status = str(task.get("effective_status") or task.get("task_status") or "")
        if status == "SUCCEEDED":
            return task
        if status == "FAILED":
            raise XiaoyuzhouAccountError(f"DashScope task failed: {task.get('message') or task.get('code') or task_id}")
        time.sleep(max(1, poll_interval))
    raise XiaoyuzhouAccountError(f"DashScope task did not finish after {max_poll_attempts} attempts: {last_task}")


def dashscope_fetch_task(*, api_key: str, task_id: str, timeout: int) -> dict[str, Any]:
    response = request_json(
        method="POST",
        url=f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable",
        },
        timeout=timeout,
    )
    return parse_dashscope_task(response)


def dashscope_download_transcript(*, transcription_url: str, timeout: int) -> dict[str, Any]:
    payload = request_json(method="GET", url=transcription_url, headers={}, timeout=timeout)
    transcripts = payload.get("transcripts")
    if not isinstance(transcripts, list):
        raise XiaoyuzhouAccountError("DashScope transcript payload is missing transcripts.")
    texts = [
        text.strip()
        for transcript in transcripts
        if isinstance(transcript, dict)
        for text in [transcript.get("text")]
        if isinstance(text, str) and text.strip()
    ]
    if not texts:
        raise XiaoyuzhouAccountError("DashScope transcript payload does not contain text.")
    return {"text": "\n\n".join(texts), "payload": payload}


def parse_dashscope_task(payload: dict[str, Any]) -> dict[str, Any]:
    output = as_mapping(payload.get("output"))
    task_id = string_value(output, "task_id")
    task_status = string_value(output, "task_status")
    if not task_id or not task_status:
        raise XiaoyuzhouAccountError("DashScope response is missing task_id or task_status.")
    result = {}
    results = output.get("results")
    if isinstance(results, list) and results and isinstance(results[0], dict):
        result = results[0]
    subtask_status = string_value(result, "subtask_status")
    return {
        "task_id": task_id,
        "task_status": task_status,
        "subtask_status": subtask_status,
        "effective_status": subtask_status or task_status,
        "transcription_url": string_value(result, "transcription_url"),
        "code": string_value(result, "code") or string_value(output, "code"),
        "message": string_value(result, "message") or string_value(output, "message"),
    }


def request_json(
    *,
    method: str,
    url: str,
    headers: dict[str, str],
    timeout: int,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    request = Request(url, data=body, method=method)
    for key, value in headers.items():
        request.add_header(key, value)
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise XiaoyuzhouAccountError(f"Request failed with HTTP {exc.code}: {raw.strip()}") from exc
    except URLError as exc:
        raise XiaoyuzhouAccountError(f"Request failed: {exc.reason}") from exc
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise XiaoyuzhouAccountError("Response has unexpected shape.")
    return parsed


def parse_raw_snapshot(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    audio_url = extract_jsonish_string(text, "audio_url")
    episode_id = extract_jsonish_string(text, "episode_id") or extract_episode_id_from_text(text)
    title = extract_frontmatter_string(text, "title") or episode_id
    episode_url = extract_frontmatter_string(text, "url") or (
        f"https://www.xiaoyuzhoufm.com/episode/{episode_id}" if episode_id else ""
    )
    podcast_title = extract_jsonish_string(text, "podcast_title") or extract_frontmatter_string(text, "author") or "Xiaoyuzhou"
    if not audio_url:
        raise XiaoyuzhouAccountError(f"Raw snapshot does not contain audio_url: {path}")
    if not episode_id:
        raise XiaoyuzhouAccountError(f"Raw snapshot does not contain episode_id: {path}")
    return {
        "audio_url": audio_url,
        "episode_id": episode_id,
        "title": title,
        "episode_url": episode_url,
        "podcast_title": podcast_title,
    }


def extract_jsonish_string(text: str, key: str) -> str:
    match = re.search(rf'"{re.escape(key)}"\s*:\s*"([^"]+)"', text)
    if match:
        return match.group(1)
    return ""


def extract_frontmatter_string(text: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}:\s*(.+)$", text, flags=re.MULTILINE)
    if not match:
        return ""
    value = match.group(1).strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        try:
            return str(json.loads(value))
        except json.JSONDecodeError:
            return value[1:-1]
    return value


def extract_episode_id_from_text(text: str) -> str:
    match = re.search(r"xiaoyuzhoufm\.com/episode/([A-Za-z0-9]+)", text)
    return match.group(1) if match else ""


def comment_text(comment: dict[str, Any]) -> str:
    return (
        string_value(comment, "text", "content", "comment")
        or nested_string(comment, ("comment", "text"))
        or nested_string(comment, ("content", "text"))
    )


def comment_user_name(comment: dict[str, Any]) -> str:
    owner = as_mapping(comment.get("owner") or comment.get("user") or comment.get("author"))
    return string_value(owner, "nickname", "name", "username") or "Unknown"


def write_raw_item(workspace: Path, item: RawItem) -> Path:
    output_dir = workspace / "raw" / "inbox"
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
        "status": "collected",
        "content_kind": "normalized-text",
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


def post_json(
    base_url: str,
    path: str,
    payload: dict[str, Any],
    *,
    timeout: int,
    access_token: str | None = None,
    extra_headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if access_token:
        headers["x-jike-access-token"] = access_token
    if extra_headers:
        headers.update(extra_headers)
    request = Request(f"{base_url.rstrip('/')}{path}", data=body, headers=headers, method="POST")
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
    except HTTPError as exc:
        raise XiaoyuzhouAccountError(f"Bridge request failed with HTTP {exc.code}: {path}") from exc
    except URLError as exc:
        raise XiaoyuzhouAccountError(f"Bridge request failed: {exc.reason}") from exc
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise XiaoyuzhouAccountError(f"Bridge returned invalid JSON for {path}.") from exc
    if not isinstance(parsed, dict):
        raise XiaoyuzhouAccountError(f"Bridge returned an unexpected payload for {path}.")
    code = parsed.get("code")
    if code not in (None, 200):
        raise XiaoyuzhouAccountError(f"Bridge request failed for {path}: {parsed.get('msg') or code}")
    return parsed


def resolve_session_path(workspace: Path, session_file: str | None) -> Path:
    if session_file:
        return Path(session_file).expanduser().resolve()
    return workspace / ".secrets" / "xiaoyuzhou_session.json"


def resolve_bridge_dir(workspace: Path, bridge_dir: str | None) -> Path:
    if bridge_dir:
        return Path(bridge_dir).expanduser().resolve()
    return workspace / DEFAULT_BRIDGE_RELATIVE_DIR


def save_session(path: Path, auth: AuthSession) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = auth.to_dict()
    payload["saved_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass


def load_session(path: Path) -> AuthSession:
    if not path.exists():
        raise XiaoyuzhouAccountError(f"Session file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise XiaoyuzhouAccountError(f"Session file has unexpected shape: {path}")
    auth = AuthSession.from_dict(data)
    if not auth.uid or not auth.access_token or not auth.refresh_token:
        raise XiaoyuzhouAccountError(f"Session file is missing required auth fields: {path}")
    return auth


def run_with_session_refresh(
    *,
    args: argparse.Namespace,
    auth: AuthSession,
    session_path: Path,
    operation: Callable[[AuthSession], T],
) -> T:
    try:
        return operation(auth)
    except XiaoyuzhouAccountError as exc:
        if "401" not in str(exc) or not auth.refresh_token:
            raise
        refreshed = refresh_auth(args.base_url, auth=auth, timeout=args.timeout)
        save_session(session_path, refreshed)
        return operation(refreshed)


def as_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def list_of_mappings(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def string_value(mapping: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def nested_string(mapping: dict[str, Any], path: tuple[str, ...]) -> str:
    current: Any = mapping
    for part in path:
        if not isinstance(current, dict):
            return ""
        current = current.get(part)
    return current.strip() if isinstance(current, str) else ""


def bool_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.lower() in {"true", "1", "yes"}
    return False


def normalize_date(value: str) -> str:
    match = re.search(r"\d{4}-\d{2}-\d{2}", value or "")
    return match.group(0) if match else ""


def date_prefix(item: RawItem) -> str:
    for candidate in (item.published_at, item.collected_at):
        if len(candidate) >= 10:
            return candidate[:10]
    return "unknown-date"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "item"


def mask_phone(value: str) -> str:
    digits = re.sub(r"\D+", "", value)
    if len(digits) < 7:
        return "***"
    return digits[:3] + "****" + digits[-4:]


if __name__ == "__main__":
    raise SystemExit(main())
