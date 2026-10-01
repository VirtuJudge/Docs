"""Validate local links, JSON examples, fences and conflict markers without dependencies."""

import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

FENCE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
LINK = re.compile(r"!?\[[^\]]*\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+[^)]*)?\)")
REFERENCE = re.compile(r"^\s*\[(?!\^)[^\]]+\]:\s*(<[^>]+>|\S+)")
CONFLICT = re.compile(r"^(?:<{7}|>{7})(?:\s|$)|^={7}$")


def validate_document(path: Path, root: Path) -> list[str]:
    errors = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return [f"{path}: cannot read UTF-8 Markdown"]
    root = root.resolve()
    fence = None
    language = ""
    start = 0
    block = []
    for number, line in enumerate(lines, 1):
        if CONFLICT.match(line):
            errors.append(f"{path}:{number}: unresolved conflict marker")
        marker = FENCE.match(line)
        if fence is not None:
            if (
                marker
                and marker[1][0] == fence[0]
                and len(marker[1]) >= len(fence)
                and not marker[2].strip()
            ):
                if language == "json":
                    try:
                        json.loads("\n".join(block))
                    except json.JSONDecodeError as error:
                        errors.append(
                            f"{path}:{start + error.lineno}: invalid JSON example"
                        )
                fence = None
                block = []
            else:
                block.append(line)
            continue
        if marker:
            fence = marker[1]
            language = marker[2].strip().lower()
            start = number
            continue
        targets = [match[1] for match in LINK.finditer(line)]
        reference = REFERENCE.match(line)
        if reference:
            targets.append(reference[1])
        for target in targets:
            parsed = urlsplit(target.strip("<>"))
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            local_path = unquote(parsed.path)
            resolved = (
                root / local_path.lstrip("/")
                if local_path.startswith("/")
                else path.parent / local_path
            ).resolve()
            if not resolved.is_relative_to(root) or not resolved.exists():
                errors.append(
                    f"{path}:{number}: missing or out-of-repository local link"
                )
    if fence is not None:
        errors.append(f"{path}:{start}: unclosed code fence")
    return errors


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    paths = subprocess.check_output(
        ["git", "ls-files", "*.md"], cwd=root, text=True
    ).splitlines()
    errors = [error for path in paths for error in validate_document(root / path, root)]
    for error in errors:
        print(error, file=sys.stderr)
    print(f"Validated {len(paths)} tracked Markdown files; {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
