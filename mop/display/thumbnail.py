from pathlib import Path
import sys
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

THUMBNAIL_WIDTH = 400
THUMBNAIL_HEIGHT = 400
VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tiff", ".webp"}


def generate_single_thumbnail(
        source_file: Path,
        target_file: Path,
        width: int = THUMBNAIL_WIDTH,
        height: int = THUMBNAIL_HEIGHT) -> bool:
    """Generate a center-cropped thumbnail."""
    try:
        target_file.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(source_file) as img:
            orig_w, orig_h = img.size
            if orig_w > 0:
                new_h = int(orig_h * (width / orig_w))
                resized = img.resize(
                    (width, new_h), Image.Resampling.LANCZOS)
            else:
                resized = img

            if resized.height > height:
                top = (resized.height - height) // 2
                cropped = resized.crop((0, top, width, top + height))
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


def ensure_thumbnail(
        filename: str,
        media_folder: Path,
        width: int = THUMBNAIL_WIDTH,
        height: int = THUMBNAIL_HEIGHT) -> Path | None:
    """Return thumbnail path, generating on-demand if it does not exist."""
    name = Path(filename).name
    flat_thumb = media_folder / 'thumbnails' / name
    if flat_thumb.exists():
        return flat_thumb

    exact_thumb = media_folder / 'thumbnails' / filename
    if exact_thumb.exists():
        return exact_thumb

    images_dir = media_folder / 'images'
    matched = list(images_dir.rglob(name))
    if not matched:
        return None

    source_path = matched[0]
    if generate_single_thumbnail(source_path, flat_thumb, width, height):
        return flat_thumb
    return None  # pragma: no cover
