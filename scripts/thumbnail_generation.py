from pathlib import Path
import sys
import time

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from mop.display.thumbnail import (  # pylint: disable=wrong-import-position
    VALID_EXTENSIONS, generate_single_thumbnail)

DEFAULT_SOURCE = ROOT_DIR / "storage" / "media" / "images"
DEFAULT_TARGET = ROOT_DIR / "storage" / "media" / "thumbnails"


def generate_all_thumbnails(
        source_dir: Path = DEFAULT_SOURCE,
        target_dir: Path = DEFAULT_TARGET,
        force: bool = False) -> dict[str, int]:
    """Scan source_dir and generate thumbnails in target_dir."""
    target_dir.mkdir(parents=True, exist_ok=True)
    created = 0
    skipped = 0

    for source_file in source_dir.rglob("*"):
        if source_file.suffix.lower() not in VALID_EXTENSIONS:
            continue

        target_file = target_dir / source_file.name

        # Skip if already exists and is newer than source
        if not force and target_file.exists():
            if target_file.stat().st_mtime >= source_file.stat().st_mtime:
                skipped += 1
                continue

        if generate_single_thumbnail(source_file, target_file):
            created += 1

    return {"created": created, "skipped": skipped}


if __name__ == "__main__":
    t0 = time.time()
    stats = generate_all_thumbnails()
    elapsed = time.time() - t0
    print(
        f"Thumbnails done in {elapsed:.2f}s: "
        f"{stats['created']} created, {stats['skipped']} up-to-date.")
