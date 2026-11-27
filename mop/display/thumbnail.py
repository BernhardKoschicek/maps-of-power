from functools import lru_cache
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

THUMBNAIL_WIDTH = 400
THUMBNAIL_HEIGHT = 400
VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tiff", ".webp"}
GLOB_METACHARS = {"*", "?", "[", "]"}
INDEX_REFRESH_TTL_SECONDS = 30.0
_index_lock = threading.Lock()
_last_index_refresh: dict[Path, float] = {}


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
                new_h = max(1, int(orig_h * (width / orig_w)))
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

            tmp_path: Path | None = None
            try:
                with tempfile.NamedTemporaryFile(
                        dir=target_file.parent,
                        suffix=target_file.suffix,
                        delete=False) as tmp_file:
                    tmp_path = Path(tmp_file.name)
                cropped.save(tmp_path)
                os.chmod(tmp_path, 0o644)
                os.replace(tmp_path, target_file)
                tmp_path = None
                return True
            finally:
                if tmp_path is not None and tmp_path.exists():
                    tmp_path.unlink(missing_ok=True)
    except Exception as exc:  # pragma: no cover
        print(f"Error creating thumbnail for {source_file}: {exc}",
              file=sys.stderr)
        return False


@lru_cache(maxsize=16)
def _build_image_index(
        images_dir: Path,
        _mtime_ns: int = 0) -> dict[str, Path]:
    """Build a cached mapping of image filename to its full path."""
    with _index_lock:
        _last_index_refresh[images_dir] = time.monotonic()
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
    try:
        dir_mtime = images_dir.stat().st_mtime_ns if images_dir.exists() else 0
    except OSError:  # pragma: no cover
        dir_mtime = 0
    image_index = _build_image_index(images_dir, dir_mtime)
    source_path = image_index.get(name)
    if not source_path or not source_path.exists():
        now = time.monotonic()
        with _index_lock:
            last_ref = _last_index_refresh.get(images_dir, 0.0)
            should_refresh = (now - last_ref) >= INDEX_REFRESH_TTL_SECONDS
            if should_refresh:
                _last_index_refresh[images_dir] = now
                _build_image_index.cache_clear()
        if should_refresh:
            image_index = _build_image_index(images_dir, dir_mtime)
            source_path = image_index.get(name)
    if not source_path or not source_path.exists():
        return None

    if generate_single_thumbnail(source_path, flat_thumb, width, height):
        return flat_thumb
    return None  # pragma: no cover
