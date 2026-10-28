#!/usr/bin/env python3
"""Check local Markdown links and skill frontmatter."""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
errors = []


def check_links():
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if target.startswith(("http://", "https://", "#", "mailto:", "tel:", "data:", "/")):
                continue
            target = target.split("#", 1)[0]
            if target and not (path.parent / target).resolve().exists():
                errors.append(f"{path.relative_to(ROOT)}: missing {target}")


def check_skills():
    skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
    for path in skills:
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            errors.append(f"{path.relative_to(ROOT)}: missing frontmatter")
            continue
        end = text.find("\n---", 4)
        if end == -1:
            errors.append(f"{path.relative_to(ROOT)}: unclosed frontmatter")
            continue
        block = text[4:end]
        name = re.search(r"^name:\s*(.+)$", block, re.M)
        if not name:
            errors.append(f"{path.relative_to(ROOT)}: missing name")
        elif name.group(1).strip() != path.parent.name:
            errors.append(
                f"{path.relative_to(ROOT)}: name {name.group(1).strip()!r} "
                f"does not match directory {path.parent.name!r}"
            )
        if not re.search(r"^description:\s*\S", block, re.M):
            errors.append(f"{path.relative_to(ROOT)}: missing description")
    return len(skills)


check_links()
skill_count = check_skills()
if errors:
    print("\n".join(errors))
    sys.exit(1)

md_count = sum(1 for p in ROOT.rglob("*.md") if ".git" not in p.parts)
print(f"docs ok: {md_count} markdown files, {skill_count} skills")
