from pathlib import Path
from wand.image import Image

ROOT_DIR = Path(__file__).resolve().parent.parent
source_folder = ROOT_DIR / "mop/static/images/projects"
target_folder = ROOT_DIR / "mop/static/thumbnails"

THUMBNAIL_WIDTH = 400
THUMBNAIL_HEIGHT = 400

target_folder.mkdir(parents=True, exist_ok=True)

for source_file in source_folder.rglob("*"):
    if source_file.suffix.lower() in {".jpg", ".jpeg", ".png", ".tiff"}:
        target_file = target_folder / source_file.name

        with Image(filename=str(source_file)) as img:
            img.transform(resize=f"{THUMBNAIL_WIDTH}x")

            if img.height > THUMBNAIL_HEIGHT:
                top = (img.height - THUMBNAIL_HEIGHT) // 2
                img.crop(
                    width=THUMBNAIL_WIDTH,
                    height=THUMBNAIL_HEIGHT,
                    left=0,
                    top=top)

            img.save(filename=str(target_file))

        print(f"Thumbnail created for {source_file}")

print("All thumbnails created successfully!")
