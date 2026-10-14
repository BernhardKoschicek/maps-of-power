from pathlib import Path
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

ROOT_DIR = Path(__file__).resolve().parent.parent
source_folder = ROOT_DIR / "mop/static/images/projects"
target_folder = ROOT_DIR / "mop/static/thumbnails"

THUMBNAIL_WIDTH = 400
THUMBNAIL_HEIGHT = 400

target_folder.mkdir(parents=True, exist_ok=True)

for source_file in source_folder.rglob("*"):
    if source_file.suffix.lower() in {".jpg", ".jpeg", ".png", ".tiff"}:
        target_file = target_folder / source_file.name

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

        print(f"Thumbnail created for {source_file}")

print("All thumbnails created successfully!")
