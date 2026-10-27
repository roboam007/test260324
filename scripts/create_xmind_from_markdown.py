import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def make_topic(title: str) -> dict:
    return {
        "id": uuid.uuid4().hex,
        "class": "topic",
        "title": title.strip(),
    }


def add_subtopic(parent: dict, title: str) -> dict:
    topic = make_topic(title)
    parent.setdefault("children", {}).setdefault("attached", []).append(topic)
    return topic


def resolve_heading_parent(heading_stack: dict, level: int, root: dict) -> dict:
    """Find nearest ancestor heading when markdown skips levels (e.g. ### → #####)."""
    if level <= 1:
        return root
    for parent_level in range(level - 1, 0, -1):
        if parent_level in heading_stack:
            return heading_stack[parent_level]
    return root


def markdown_to_xmind(md_path: Path, xmind_path: Path) -> None:
    lines = md_path.read_text(encoding="utf-8").splitlines()

    if xmind_path.exists():
        xmind_path.unlink()

    root = make_topic(md_path.stem)
    heading_stack = {}
    bullet_stacks = {}
    current_leaf = None

    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            continue

        heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        bullet_match = re.match(r"^(\s*)-\s+(.+)$", line)

        if heading_match:
            level = len(heading_match.group(1))
            title = heading_match.group(2).strip()

            if level == 1:
                root["title"] = title
                heading_stack = {1: root}
                current_leaf = root
                continue

            parent = resolve_heading_parent(heading_stack, level, root)
            node = add_subtopic(parent, title)
            heading_stack[level] = node

            for deep_level in list(heading_stack.keys()):
                if deep_level > level:
                    del heading_stack[deep_level]

            current_leaf = node
            continue

        if bullet_match:
            indent = len(bullet_match.group(1))
            text = bullet_match.group(2).strip()

            bullet_level = indent // 2 + 1
            base_parent = current_leaf if current_leaf is not None else root

            key = id(base_parent)
            if key not in bullet_stacks:
                bullet_stacks[key] = {}
            bullet_stack = bullet_stacks[key]

            if bullet_level == 1:
                node = add_subtopic(base_parent, text)
                bullet_stack[1] = node
            else:
                parent = bullet_stack.get(bullet_level - 1, base_parent)
                node = add_subtopic(parent, text)
                bullet_stack[bullet_level] = node

            for deep_level in list(bullet_stack.keys()):
                if deep_level > bullet_level:
                    del bullet_stack[deep_level]

    sheet_id = uuid.uuid4().hex
    content = [
        {
            "id": sheet_id,
            "class": "sheet",
            "title": "Test Cases",
            "rootTopic": root,
            "topicPositioning": "fixed",
        }
    ]
    metadata = {
        "creator": {
            "name": "test_case_gen",
            "version": "1.0.0",
        },
        "created": datetime.now(timezone.utc).isoformat(),
        "activeSheetId": sheet_id,
    }
    manifest = {
        "file-entries": {
            "content.json": {},
            "metadata.json": {},
            "manifest.json": {},
        }
    }

    with ZipFile(xmind_path, "w", ZIP_DEFLATED) as archive:
        archive.writestr(
            "content.json",
            json.dumps(content, ensure_ascii=False, separators=(",", ":")),
        )
        archive.writestr(
            "metadata.json",
            json.dumps(metadata, ensure_ascii=False, separators=(",", ":")),
        )
        archive.writestr(
            "manifest.json",
            json.dumps(manifest, ensure_ascii=False, separators=(",", ":")),
        )


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 create_xmind_from_markdown.py <test_cases.md>")
        print('Example: python3 create_xmind_from_markdown.py "./aixpay_oboss_user_tag_test_cases.md"')
        sys.exit(1)

    md_file = Path(sys.argv[1]).expanduser()
    if not md_file.is_absolute():
        md_file = Path.cwd() / md_file
    md_file = md_file.resolve()

    if not md_file.exists():
        print(f"Error: markdown file not found: {md_file}")
        sys.exit(1)

    xmind_file = md_file.with_suffix(".xmind")
    markdown_to_xmind(md_file, xmind_file)
    print(f"Generated: {xmind_file}")
