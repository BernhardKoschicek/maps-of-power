"""Unit and integration tests for thumbnail generation and serving."""

from pathlib import Path
from flask.testing import FlaskClient
from PIL import Image

from mop.display.thumbnail import (
    ensure_thumbnail, generate_single_thumbnail)
from scripts.thumbnail_generation import generate_all_thumbnails


def test_generate_single_thumbnail(tmp_path: Path) -> None:
    """Test generating single thumbnail for landscape and portrait images."""
    src_landscape = tmp_path / "test_orig.png"
    img = Image.new("RGBA", (800, 600), color=(255, 0, 0, 128))
    img.save(src_landscape)

    target_jpg = tmp_path / "test_thumb.jpg"
    success = generate_single_thumbnail(
        src_landscape, target_jpg, width=100, height=100)
    assert success is True
    assert target_jpg.exists()
    with Image.open(target_jpg) as out:
        assert out.size == (100, 75)
        assert out.mode == "RGB"

    src_portrait = tmp_path / "test_portrait.png"
    img_portrait = Image.new("RGB", (600, 800), color=(0, 0, 255))
    img_portrait.save(src_portrait)

    target_portrait = tmp_path / "test_thumb_portrait.jpg"
    success_p = generate_single_thumbnail(
        src_portrait, target_portrait, width=100, height=100)
    assert success_p is True
    with Image.open(target_portrait) as out_p:
        assert out_p.size == (100, 100)


def test_ensure_thumbnail_on_demand(tmp_path: Path) -> None:
    """Test on-demand thumbnail generation via ensure_thumbnail."""
    media_dir = tmp_path / "media"
    images_dir = media_dir / "images" / "sub"
    images_dir.mkdir(parents=True)
    thumbs_dir = media_dir / "thumbnails"
    thumbs_dir.mkdir(parents=True)

    src = images_dir / "sample.jpg"
    img = Image.new("RGB", (200, 400), color=(0, 255, 0))
    img.save(src)

    # Missing thumbnail should be generated on-demand
    res_path = ensure_thumbnail("sample.jpg", media_dir, width=50, height=50)
    assert res_path is not None
    assert res_path.exists()
    assert res_path.name == "sample.jpg"

    # Second call hits cache
    res_cached = ensure_thumbnail(
        "sample.jpg", media_dir, width=50, height=50)
    assert res_cached == res_path

    # Non-existent image returns None
    missing = ensure_thumbnail(
        "nonexistent.jpg", media_dir, width=50, height=50)
    assert missing is None


def test_generate_all_thumbnails_script(tmp_path: Path) -> None:
    """Test bulk generation script with incremental skipping."""
    source_dir = tmp_path / "images"
    target_dir = tmp_path / "thumbnails"
    source_dir.mkdir()

    src1 = source_dir / "img1.png"
    Image.new("RGB", (100, 100), color=(10, 20, 30)).save(src1)

    # First run generates
    stats1 = generate_all_thumbnails(source_dir, target_dir)
    assert stats1["created"] == 1
    assert stats1["skipped"] == 0

    # Second run skips up-to-date
    stats2 = generate_all_thumbnails(source_dir, target_dir)
    assert stats2["created"] == 0
    assert stats2["skipped"] == 1

    # Forced run re-generates
    stats3 = generate_all_thumbnails(source_dir, target_dir, force=True)
    assert stats3["created"] == 1


def test_serve_media_thumbnails_endpoint(client: FlaskClient) -> None:
    """Test /media/thumbnails/<filename> and on-demand generation."""
    res = client.get('/media/thumbnails/altwege_2014.jpg')
    assert res.status_code == 200
    assert res.content_type.startswith('image/')
    assert len(res.data) > 0
    res.close()
