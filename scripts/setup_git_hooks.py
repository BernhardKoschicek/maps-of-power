#!/usr/bin/env python3
"""Install repository git hooks (e.g. post-merge thumbnail generation)."""

from pathlib import Path
import stat

ROOT_DIR = Path(__file__).resolve().parent.parent
HOOKS_DIR = ROOT_DIR / ".git" / "hooks"

POST_MERGE_SCRIPT = """#!/bin/sh
# Automatically update thumbnails on git pull / merge
echo "Running thumbnail generator..."
if command -v uv >/dev/null 2>&1; then
    uv run python scripts/thumbnail_generation.py
elif command -v python3 >/dev/null 2>&1; then
    python3 scripts/thumbnail_generation.py
fi
"""


def install_hooks() -> None:
    if not HOOKS_DIR.exists():
        print(f"Hooks directory {HOOKS_DIR} not found. Skipping.")
        return

    exec_bits = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    post_merge = HOOKS_DIR / "post-merge"
    post_merge.write_text(POST_MERGE_SCRIPT, encoding="utf-8")
    post_merge.chmod(post_merge.stat().st_mode | exec_bits)

    post_checkout = HOOKS_DIR / "post-checkout"
    post_checkout.write_text(POST_MERGE_SCRIPT, encoding="utf-8")
    post_checkout.chmod(post_checkout.stat().st_mode | exec_bits)

    print("Successfully installed git hooks: post-merge, post-checkout")


if __name__ == "__main__":
    install_hooks()
