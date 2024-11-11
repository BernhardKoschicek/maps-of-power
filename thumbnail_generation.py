from pathlib import Path
from wand.image import Image

source_folder = Path("mop/static/images/projects")
target_folder = Path("mop/static/thumbnails")

thumbnail_width = 400
thumbnail_height = 400

target_folder.mkdir(parents=True, exist_ok=True)

for source_file in source_folder.rglob("*"):
    if source_file.suffix.lower() in {".jpg", ".jpeg", ".png", ".tiff"}:
        target_file = target_folder / source_file.name

        with Image(filename=str(source_file)) as img:
            img.transform(resize=f"{thumbnail_width}x")

            if img.height > thumbnail_height:
                top = (img.height - thumbnail_height) // 2
                img.crop(width=thumbnail_width, height=thumbnail_height, left=0, top=top)

            img.save(filename=str(target_file))

        print(f"Thumbnail created for {source_file}")

print("All thumbnails created successfully!")
