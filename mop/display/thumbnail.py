from functools import lru_cache
from pathlib import Path
import sys
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

THUMBNAIL_WIDTH = 400
THUMBNAIL_HEIGHT = 400
VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tiff", ".webp"}
GLOB_METACHARS = {"*", "?", "[", "]"}


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


@lru_cache(maxsize=16)
def _build_image_index(images_dir: Path) -> dict[str, Path]:
    """Build a cached mapping of image filename to its full path."""
    if not images_dir.exists():
        return {}
    index: dict[str, Path] = {}
    for path in images_dir.rglob('*'):
        if (path.is_file()
                and path.suffix.lower() in VALID_EXTENSIONS
                and path.name not in index):
            index[path.name] = path
    return index


def ensure_thumbnail(
        filename: str,
        media_folder: Path,
        width: int = THUMBNAIL_WIDTH,
        height: int = THUMBNAIL_HEIGHT) -> Path | None:
    """Return thumbnail path, generating on-demand if it does not exist."""
    name = Path(filename).name
    if (not name
            or any(c in name for c in GLOB_METACHARS)
            or Path(name).suffix.lower() not in VALID_EXTENSIONS):
        return None

    thumbs_root = (media_folder / 'thumbnails').resolve()
    flat_thumb = thumbs_root / name
    if flat_thumb.exists():
        return flat_thumb

    exact_thumb = (thumbs_root / filename).resolve()
    if exact_thumb.is_relative_to(thumbs_root) and exact_thumb.exists():
        return exact_thumb

    images_dir = (media_folder / 'images').resolve()
    image_index = _build_image_index(images_dir)
    source_path = image_index.get(name)
    if not source_path or not source_path.exists():
        return None

    if generate_single_thumbnail(source_path, flat_thumb, width, height):
        return flat_thumb
    return None  # pragma: no cover
