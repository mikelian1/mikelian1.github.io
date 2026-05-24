#!/usr/bin/env python3
"""
Convert a Typora markdown note into a Jekyll blog post.

This script handles the common differences between Typora/GitHub-flavored
notes and this Academic Pages/Jekyll site:

1. Normalize display math blocks so MathJax can parse standalone $$ blocks.
2. Copy local markdown/html image assets into the public images directory.
3. Convert GitHub/Obsidian callouts such as > [!NOTE] into notice blocks.
4. Add Jekyll front matter when the source note does not already have it.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import date
from pathlib import Path
from urllib.parse import unquote, urlparse


CALLOUT_CLASSES = {
    "NOTE": "notice--info",
    "TIP": "notice--success",
    "IMPORTANT": "notice--primary",
    "WARNING": "notice--warning",
    "CAUTION": "notice--danger",
}


def split_front_matter(text: str) -> tuple[str | None, str]:
    """Return existing YAML front matter and body."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text

    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            front_matter = "\n".join(lines[: index + 1])
            body = "\n".join(lines[index + 1 :])
            return front_matter, body

    return None, text


def extract_title(body: str, source: Path) -> str:
    """Use the first H1 as title, otherwise use the filename."""
    for line in body.splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line)
        if match:
            return match.group(1).strip()

    stem = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", source.stem)
    return stem.replace("-", " ").replace("_", " ").strip() or "Untitled Post"


def slugify(value: str, fallback: str = "post") -> str:
    """Create a conservative URL slug."""
    value = value.lower().strip()
    value = re.sub(r"[\s_]+", "-", value)
    value = re.sub(r"[^a-z0-9-]+", "", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or fallback


def make_front_matter(title: str, post_date: str, slug: str, tags: list[str]) -> str:
    year, month, _ = post_date.split("-")
    permalink = f"/posts/{year}/{month}/{slug}/"
    lines = [
        "---",
        f'title: "{title}"',
        f"date: {post_date}",
        f"permalink: {permalink}",
    ]

    if tags:
        lines.append("tags:")
        lines.extend(f"  - {tag}" for tag in tags)

    lines.append("---")
    return "\n".join(lines)


def is_fence_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("```") or stripped.startswith("~~~")


def convert_callouts(text: str) -> str:
    """Convert > [!NOTE] style callouts into Academic Pages notice blocks."""
    lines = text.splitlines()
    output: list[str] = []
    index = 0
    in_fence = False

    callout_pattern = re.compile(
        r"^>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\][+-]?\s*(.*?)\s*$",
        re.IGNORECASE,
    )

    while index < len(lines):
        line = lines[index]

        if is_fence_line(line):
            in_fence = not in_fence
            output.append(line)
            index += 1
            continue

        match = None if in_fence else callout_pattern.match(line)
        if not match:
            output.append(line)
            index += 1
            continue

        kind = match.group(1).upper()
        title = match.group(2).strip()
        notice_class = CALLOUT_CLASSES[kind]
        label = kind.title()
        body: list[str] = []
        index += 1

        while index < len(lines):
            current = lines[index]
            if current.startswith(">"):
                body.append(re.sub(r"^>\s?", "", current))
                index += 1
                continue
            break

        while body and not body[0].strip():
            body.pop(0)
        while body and not body[-1].strip():
            body.pop()

        output.append(f'<div class="{notice_class}" markdown="1">')
        heading = f"**{label}:**"
        if title:
            heading += f" {title}"
        output.append(heading)
        if body:
            output.append("")
            output.extend(body)
        output.append("</div>")

    return "\n".join(output) + ("\n" if text.endswith("\n") else "")


def normalize_display_math(text: str) -> str:
    """Make standalone $$ blocks parse reliably after Jekyll markdown rendering."""
    lines = text.splitlines()
    output: list[str] = []
    in_fence = False
    in_math = False

    for line in lines:
        if is_fence_line(line) and not in_math:
            in_fence = not in_fence
            output.append(line)
            continue

        if in_fence:
            output.append(line)
            continue

        if line.strip() == "$$":
            if not in_math:
                if output and output[-1].strip():
                    output.append("")
                output.append("$$")
                in_math = True
            else:
                output.append("$$")
                output.append("")
                in_math = False
            continue

        if in_math and not line.strip():
            continue

        output.append(line)

    while output and not output[-1].strip():
        output.pop()

    return "\n".join(output) + "\n"


def split_markdown_link_target(raw: str) -> tuple[str, str]:
    """Split a markdown link target into destination and optional title."""
    target = raw.strip()
    if target.startswith("<"):
        end = target.find(">")
        if end != -1:
            return target[1:end], target[end + 1 :].strip()

    quote_match = re.match(r"^(\S+)(\s+['\"].*['\"])\s*$", target)
    if quote_match:
        return quote_match.group(1), quote_match.group(2).strip()

    return target, ""


def should_skip_asset(path_text: str) -> bool:
    parsed = urlparse(path_text)
    if parsed.scheme and parsed.scheme not in {"file"}:
        return True
    if path_text.startswith("#"):
        return True
    if path_text.startswith("/") and not Path(path_text).exists():
        return True
    return False


def resolve_asset_path(path_text: str, source_md: Path, repo_root: Path) -> Path | None:
    parsed = urlparse(path_text)
    if parsed.scheme == "file":
        candidate = Path(unquote(parsed.path)).expanduser()
        return candidate if candidate.exists() else None

    decoded = unquote(path_text)
    candidate = Path(decoded).expanduser()
    if candidate.is_absolute():
        return candidate if candidate.exists() else None

    candidates = [
        source_md.parent / candidate,
        repo_root / candidate,
    ]
    for item in candidates:
        if item.exists():
            return item.resolve()
    return None


def unique_destination(asset_dir: Path, filename: str, source: Path) -> Path:
    """Return a non-conflicting destination for an asset."""
    destination = asset_dir / filename
    if not destination.exists() or destination.resolve() == source.resolve():
        return destination

    stem = destination.stem
    suffix = destination.suffix
    counter = 2
    while True:
        candidate = asset_dir / f"{stem}-{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def copy_asset(
    path_text: str,
    source_md: Path,
    repo_root: Path,
    asset_dir: Path,
    copied: dict[Path, str],
) -> str | None:
    """Copy a local asset and return its site-root URL path."""
    if should_skip_asset(path_text):
        return None

    source = resolve_asset_path(path_text, source_md, repo_root)
    if source is None or not source.is_file():
        return None

    source = source.resolve()
    if source not in copied:
        destination = unique_destination(asset_dir, source.name, source)
        asset_dir.mkdir(parents=True, exist_ok=True)
        if destination.resolve() != source:
            shutil.copy2(source, destination)
        copied[source] = "/" + destination.relative_to(repo_root).as_posix()

    return copied[source]


def rewrite_markdown_images(
    text: str,
    source_md: Path,
    repo_root: Path,
    asset_dir: Path,
    copied: dict[Path, str],
) -> str:
    pattern = re.compile(r"!\[([^\]]*)\]\(([^)\n]+)\)")

    def replace(match: re.Match[str]) -> str:
        alt = match.group(1)
        raw_target = match.group(2)
        destination, title = split_markdown_link_target(raw_target)
        new_url = copy_asset(destination, source_md, repo_root, asset_dir, copied)
        if new_url is None:
            return match.group(0)
        title_part = f" {title}" if title else ""
        return f"![{alt}]({new_url}{title_part})"

    return pattern.sub(replace, text)


def rewrite_html_images(
    text: str,
    source_md: Path,
    repo_root: Path,
    asset_dir: Path,
    copied: dict[Path, str],
) -> str:
    pattern = re.compile(r'(<img\b[^>]*?\bsrc=["\'])([^"\']+)(["\'][^>]*>)', re.IGNORECASE)

    def replace(match: re.Match[str]) -> str:
        new_url = copy_asset(match.group(2), source_md, repo_root, asset_dir, copied)
        if new_url is None:
            return match.group(0)
        return f"{match.group(1)}{new_url}{match.group(3)}"

    return pattern.sub(replace, text)


def parse_tags(values: list[str]) -> list[str]:
    tags: list[str] = []
    for value in values:
        for item in value.split(","):
            tag = item.strip()
            if tag:
                tags.append(tag)
    return tags


def convert(args: argparse.Namespace) -> Path:
    repo_root = Path(args.repo_root).expanduser().resolve()
    source_md = Path(args.input).expanduser().resolve()
    if not source_md.exists():
        raise FileNotFoundError(f"Input file does not exist: {source_md}")

    raw_text = source_md.read_text(encoding="utf-8")
    existing_front_matter, body = split_front_matter(raw_text)
    title = args.title or extract_title(body, source_md)
    post_date = args.date
    slug = args.slug or slugify(source_md.stem)
    tags = parse_tags(args.tag)

    if args.output:
        output_path = Path(args.output).expanduser()
        if not output_path.is_absolute():
            output_path = repo_root / output_path
    else:
        output_path = repo_root / args.post_dir / f"{post_date}-{slug}.md"

    if args.asset_dir:
        asset_dir = Path(args.asset_dir).expanduser()
        if not asset_dir.is_absolute():
            asset_dir = repo_root / asset_dir
    else:
        asset_dir = repo_root / args.image_root / slug

    copied: dict[Path, str] = {}
    body = convert_callouts(body)
    body = normalize_display_math(body)
    body = rewrite_markdown_images(body, source_md, repo_root, asset_dir, copied)
    body = rewrite_html_images(body, source_md, repo_root, asset_dir, copied)

    front_matter = existing_front_matter
    if front_matter is None or args.replace_front_matter:
        front_matter = make_front_matter(title, post_date, slug, tags)

    final_text = f"{front_matter}\n\n{body.rstrip()}\n"

    if output_path.exists() and not args.overwrite:
        raise FileExistsError(
            f"Output already exists: {output_path}. Use --overwrite to replace it."
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(final_text, encoding="utf-8")

    print(f"Wrote post: {output_path.relative_to(repo_root)}")
    if copied:
        print(f"Copied images: {asset_dir.relative_to(repo_root)}")
    return output_path


def build_parser() -> argparse.ArgumentParser:
    repo_root = Path(__file__).resolve().parents[1]
    today = date.today().isoformat()
    parser = argparse.ArgumentParser(
        description="Convert a Typora markdown note into a Jekyll post.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/typora_to_jekyll_post.py notes/flow.md --title \"Flow Matching Lecture 1\" --slug flow-matching-lecture1 --tag \"flow matching\"\n"
            "  python scripts/typora_to_jekyll_post.py notes/flow.md --slug flow-matching-lecture1 --overwrite\n"
        ),
    )
    parser.add_argument("input", help="Source Typora markdown file.")
    parser.add_argument("--title", help="Post title. Defaults to first H1 or filename.")
    parser.add_argument("--date", default=today, help=f"Post date. Default: {today}.")
    parser.add_argument("--slug", help="URL/file slug. Defaults to slugified filename.")
    parser.add_argument(
        "--tag",
        action="append",
        default=[],
        help="Post tag. Can be repeated or comma-separated.",
    )
    parser.add_argument(
        "--output",
        help="Output markdown path. Default: _posts/YYYY-MM-DD-slug.md.",
    )
    parser.add_argument("--post-dir", default="_posts", help="Jekyll post directory.")
    parser.add_argument("--image-root", default="images", help="Public image root.")
    parser.add_argument(
        "--asset-dir",
        help="Directory for copied images. Default: images/slug.",
    )
    parser.add_argument(
        "--replace-front-matter",
        action="store_true",
        help="Replace existing front matter instead of preserving it.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite output file if it already exists.",
    )
    parser.add_argument(
        "--repo-root",
        default=str(repo_root),
        help="Repository root. Defaults to this script's parent repository.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        convert(args)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
