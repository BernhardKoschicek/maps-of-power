from pathlib import Path
import sys
import time
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = ROOT_DIR / "storage" / "media" / "images"
DEFAULT_TARGET = ROOT_DIR / "storage" / "media" / "thumbnails"

THUMBNAIL_WIDTH = 400
THUMBNAIL_HEIGHT = 400
VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tiff", ".webp"}


def generate_single_thumbnail(source_file: Path, target_file: Path) -> bool:
    """Generate a single 400x400 center-cropped thumbnail."""
    try:
        target_file.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(source_file) as img:
            orig_w, orig_h = img.size
            if orig_w > 0:
                new_h = int(orig_h * (THUMBNAIL_WIDTH / orig_w))
                resized = img.resize(
                    (THUMBNAIL_WIDTH, new_h), Image.Resampling.LANCZOS)
            else:
                resized = img

            if resized.height > THUMBNAIL_HEIGHT:
                top = (resized.height - THUMBNAIL_HEIGHT) // 2
                cropped = resized.crop(
                    (0, top, THUMBNAIL_WIDTH, top + THUMBNAIL_HEIGHT))
            else:
                cropped = resized

            if (cropped.mode in ("RGBA", "P")
                    and target_file.suffix.lower() in {".jpg", ".jpeg"}):
                cropped = cropped.convert("RGB")

            cropped.save(target_file)
            return True
    except Exception as exc:  # pragma: no cover
        print(f"Error creating thumbnail for {source_file}: {exc}",
              file=sys.stderr)
        return False


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
