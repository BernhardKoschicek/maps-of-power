"""Tests for media serving and legacy static aliases."""

from flask.testing import FlaskClient


def test_serve_media_direct(client: FlaskClient) -> None:
    """Test direct /media/ endpoint."""
    res = client.get('/media/images/institutes/TIB-logo.png')
    assert res.status_code == 200
    assert res.content_type.startswith('image/')
    assert len(res.data) > 0
    res.close()

    res_404 = client.get('/media/images/nonexistent_file_xyz.png')
    assert res_404.status_code == 404
    res_404.close()


def test_serve_legacy_images_alias(client: FlaskClient) -> None:
    """Test legacy /static/images/... alias to storage/media/images/."""
    res = client.get('/static/images/institutes/TIB-logo.png')
    assert res.status_code == 200
    assert res.content_type.startswith('image/')
    assert len(res.data) > 0
    res.close()

    res_404 = client.get('/static/images/nonexistent_file_xyz.png')
    assert res_404.status_code == 404
    res_404.close()


def test_serve_legacy_thumbnails_alias(client: FlaskClient) -> None:
    """Test legacy /static/thumbnails/... alias to thumbnails."""
    res = client.get('/static/thumbnails/altwege_2014.jpg')
    assert res.status_code == 200
    assert res.content_type.startswith('image/')
    assert len(res.data) > 0
    res.close()

    res_404 = client.get('/static/thumbnails/nonexistent_thumb_xyz.jpg')
    assert res_404.status_code == 404
    res_404.close()


def test_serve_legacy_repository_alias(client: FlaskClient) -> None:
    """Test legacy /static/repository/... alias to repository folder."""
    res = client.get('/static/repository/Popovic_11_22.pdf')
    assert res.status_code == 200
    assert 'pdf' in res.content_type.lower()
    assert len(res.data) > 0
    res.close()

    res_404 = client.get('/static/repository/nonexistent_paper_xyz.pdf')
    assert res_404.status_code == 404
    res_404.close()


def test_serve_books_scans(client: FlaskClient) -> None:
    """Test book scans serving via /media/books/ and legacy aliases."""
    res_media = client.get('/media/books/tib1/TIB1_Seite_001.jpg')
    assert res_media.status_code == 200
    assert res_media.content_type.startswith('image/')
    assert len(res_media.data) > 0
    res_media.close()

    res_legacy = client.get(
        '/static/repository/books/tib1/TIB1_Seite_001.jpg')
    assert res_legacy.status_code == 200
    assert res_legacy.content_type.startswith('image/')
    assert len(res_legacy.data) > 0
    res_legacy.close()

    res_404 = client.get('/media/books/tib1/nonexistent_page.jpg')
    assert res_404.status_code == 404
    res_404.close()


def test_ui_static_assets_still_served(client: FlaskClient) -> None:
    """Test UI assets in mop/static/ (favicon, css) served via /static/."""
    res_favicon = client.get('/static/favicon.ico')
    assert res_favicon.status_code == 200
    assert len(res_favicon.data) > 0
    res_favicon.close()

    res_manifest = client.get('/static/site.webmanifest')
    assert res_manifest.status_code == 200
    assert len(res_manifest.data) > 0
    res_manifest.close()


def test_serve_video(client: FlaskClient) -> None:
    """Test video serving via /media/videos/ and legacy /static/videos/."""
    res_direct = client.get('/media/videos/hero.mp4')
    if res_direct.status_code == 200:
        assert 'video' in res_direct.content_type.lower()
        res_direct.close()

        res_legacy = client.get('/static/videos/hero.mp4')
        assert res_legacy.status_code == 200
        assert 'video' in res_legacy.content_type.lower()
        res_legacy.close()
    else:
        res_direct.close()
