#!/usr/bin/env python3
"""Upload an XMind file to Tyr. Auth is resolved at runtime and never persisted."""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

TYR_IMPORT_URL = "https://case.atomecorp.net/api/mind/import"
TYR_PROJECT_LIST_URL = "https://case.atomecorp.net/api/project/list"
TYR_VIEW_URL = "https://case.atomecorp.net/brainmap/40"
PROJECT_ID = "40"
FOLDER_ID = "-1"
MIND_VERSION = "0"
AUTH_HINT = (
    "打开 https://case.atomecorp.net，按 F12 → Application → Cookies，"
    "复制 case.atomecorp.net 下的 Test-Token（以及 ADVSSO）"
)

AUTH_MARKERS = (
    "unauthorized",
    "unauthorised",
    "forbidden",
    "token",
    "auth",
    "login",
    "鉴权",
    "未登录",
    "登录",
    "过期",
    "no authorization",
)


def emit(payload: dict, exit_code: int) -> None:
    print(json.dumps(payload, ensure_ascii=False))
    raise SystemExit(exit_code)


def build_title(prd_name: str) -> str:
    name = prd_name.strip()
    name = re.sub(r"^\[PRD\]\s*", "", name, flags=re.IGNORECASE)
    name = re.sub(
        r"[\[【(]\s*\d{4}-\d{2}-\d{2}(?:[ T]\d{1,2}:\d{2}(?::\d{2})?)?\s*[\]】)]",
        " ",
        name,
    )
    name = re.sub(
        r"\b\d{4}-\d{2}-\d{2}(?:[ T]\d{1,2}:\d{2}(?::\d{2})?)?\b",
        " ",
        name,
    )
    name = re.sub(r"\s+", " ", name).strip(" -_|")
    if re.match(r"^AIX\s+", name, flags=re.IGNORECASE):
        return f"AIX {name[3:].strip()}"
    return f"AIX {name}"


def is_auth_error(http_code: int, body: str, parsed: Optional[dict]) -> bool:
    if http_code in {401, 403}:
        return True
    if parsed and parsed.get("code") in {100, "100", 401, "401", 403, "403"}:
        return True
    text = body.lower()
    if any(marker in text for marker in AUTH_MARKERS):
        if parsed is None or parsed.get("code") not in {0, "0", None}:
            return True
    if parsed and parsed.get("code") not in {0, "0", None}:
        msg = str(parsed.get("msg") or parsed.get("message") or "").lower()
        if any(marker in msg for marker in AUTH_MARKERS):
            return True
    return False


def cookies_from_chrome() -> dict:
    try:
        import browser_cookie3
    except ImportError:
        return {}
    try:
        jar = browser_cookie3.chrome(domain_name="case.atomecorp.net")
    except Exception:
        return {}
    found = {}
    for cookie in jar:
        host = (cookie.domain or "").lstrip(".")
        if host.endswith("case.atomecorp.net") and cookie.name in {"Test-Token", "ADVSSO"}:
            if cookie.value:
                found[cookie.name] = cookie.value
    return found


def resolve_auth() -> dict:
    token = (os.environ.get("TYR_TOKEN") or "").strip()
    advsso = (os.environ.get("TYR_ADVSSO") or "").strip()
    source = "env" if token else None

    if not token or not advsso:
        chrome = cookies_from_chrome()
        if not token and chrome.get("Test-Token"):
            token = chrome["Test-Token"]
            source = "chrome"
        if not advsso and chrome.get("ADVSSO"):
            advsso = chrome["ADVSSO"]
            if source is None:
                source = "chrome"

    if not token:
        emit({"ok": False, "error": "AUTH_REQUIRED", "message": AUTH_HINT}, 2)

    cookie_parts = [f"Test-Token={token}"]
    if advsso:
        cookie_parts.append(f"ADVSSO={advsso}")
    return {
        "token": token,
        "cookie": "; ".join(cookie_parts),
        "source": source or "env",
        "hasAdvsso": bool(advsso),
    }


def parse_curl_output(stdout: str, stderr: str) -> tuple:
    raw = stdout.rstrip("\n")
    if "\n" in raw:
        body, http_code_str = raw.rsplit("\n", 1)
    else:
        body, http_code_str = raw, "0"
    try:
        http_code = int(http_code_str)
    except ValueError:
        body, http_code = raw, 0
    parsed = None
    if body.strip():
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = None
    return http_code, body, parsed, stderr.strip()


def curl_json(url: str, auth: dict, extra_args: Optional[list] = None) -> tuple:
    cmd = [
        "curl",
        "--url",
        url,
        "-H",
        f"authorization: {auth['token']}",
        "-H",
        f"project-id: {PROJECT_ID}",
        "-H",
        f"Cookie: {auth['cookie']}",
        "-sS",
        "-w",
        "\n%{http_code}",
    ]
    if extra_args:
        cmd[3:3] = extra_args
    try:
        completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        emit({"ok": False, "error": "CURL_MISSING", "message": "curl 未安装"}, 1)
    if completed.returncode != 0 and not completed.stdout.strip():
        emit(
            {
                "ok": False,
                "error": "CURL_FAILED",
                "message": completed.stderr.strip() or "curl 调用失败",
            },
            1,
        )
    http_code, body, parsed, err = parse_curl_output(completed.stdout, completed.stderr)
    if is_auth_error(http_code, body, parsed):
        emit(
            {
                "ok": False,
                "error": "AUTH_REQUIRED",
                "httpCode": http_code,
                "authSource": auth["source"],
                "message": AUTH_HINT,
            },
            2,
        )
    return http_code, body, parsed, err


def probe_auth(auth: dict) -> None:
    http_code, body, parsed, _err = curl_json(TYR_PROJECT_LIST_URL, auth)
    if parsed and parsed.get("code") in {0, "0"}:
        names = []
        data = parsed.get("data") or []
        if isinstance(data, list):
            names = [item.get("name") for item in data if isinstance(item, dict)]
        emit(
            {
                "ok": True,
                "probed": True,
                "authSource": auth["source"],
                "hasAdvsso": auth["hasAdvsso"],
                "projects": names,
            },
            0,
        )
    emit(
        {
            "ok": False,
            "error": "PROBE_FAILED",
            "httpCode": http_code,
            "message": body or "鉴权探测失败",
        },
        1,
    )


def run_upload(xmind_path: Path, title: str, prd_url: str, auth: dict) -> None:
    description_list = json.dumps(
        [{"content": title, "link": prd_url}],
        ensure_ascii=False,
        separators=(",", ":"),
    )
    extra = [
        "-F",
        f"file=@{xmind_path};type=application/vnd.xmind.workbook",
        "-F",
        f"title={title}",
        "-F",
        f"descriptionList={description_list}",
        "-F",
        f"mindVersion={MIND_VERSION}",
        "-F",
        f"projectId={PROJECT_ID}",
        "-F",
        "mindId=",
        "-F",
        f"folderId={FOLDER_ID}",
    ]
    http_code, body, parsed, err = curl_json(TYR_IMPORT_URL, auth, extra)
    if parsed and parsed.get("code") in {0, "0"} and str(parsed.get("msg", "")).lower() in {"success", ""}:
        emit(
            {
                "ok": True,
                "mindId": parsed.get("data"),
                "title": title,
                "authSource": auth["source"],
                "viewUrl": TYR_VIEW_URL,
            },
            0,
        )
    emit(
        {
            "ok": False,
            "error": "UPLOAD_FAILED",
            "httpCode": http_code,
            "message": body or err or "上传失败",
        },
        1,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload XMind to Tyr")
    parser.add_argument("--file", help="Path to .xmind file")
    parser.add_argument("--prd-name", help="PRD document name")
    parser.add_argument("--prd-url", help="PRD document URL")
    parser.add_argument(
        "--probe",
        action="store_true",
        help="Only verify auth against /api/project/list, do not upload",
    )
    args = parser.parse_args()

    auth = resolve_auth()

    if args.probe:
        probe_auth(auth)

    if not args.file or not args.prd_name or not args.prd_url:
        emit(
            {
                "ok": False,
                "error": "INVALID_ARGS",
                "message": "需要 --file --prd-name --prd-url，或使用 --probe 只做鉴权探测",
            },
            1,
        )

    xmind_path = Path(args.file).expanduser()
    if not xmind_path.is_absolute():
        xmind_path = Path.cwd() / xmind_path
    xmind_path = xmind_path.resolve()
    if not xmind_path.exists():
        emit({"ok": False, "error": "FILE_NOT_FOUND", "message": str(xmind_path)}, 1)

    title = build_title(args.prd_name)
    run_upload(xmind_path, title, args.prd_url.strip(), auth)


if __name__ == "__main__":
    main()
