"""Automated asset, link, and static/media server-parity integrity tests.

Ensures that:
1. No template or display helper uses url_for('static', ...) for media files
   (images, thumbnails, repository, videos, books) that live in storage/media/.
2. All media assets referenced in mop/data/ dictionaries exist in
   storage/media/.
3. All CSS url(...) references in mop/static/css/ resolve to existing files.
4. All rendered HTML pages only reference /static/... files that physically
   exist in mop/static/ (preventing 404s behind Nginx/Apache static aliases)
   and /media/... files that return HTTP 200.
"""

from pathlib import Path
import re
from typing import Any

from mop import app
from mop.data.events import event_list
from mop.data.histgeo import lectures, newsletters, volumes
from mop.data.images import category_images
from mop.data.literature import literatures
from mop.data.presentations import presentations
from mop.data.projects.projects import project_data
from mop.model.tib_db import get_volume_metadata

ROOT_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT_DIR / 'mop' / 'static'
TEMPLATES_DIR = ROOT_DIR / 'mop' / 'templates'
DISPLAY_DIR = ROOT_DIR / 'mop' / 'display'
MEDIA_DIR = ROOT_DIR / 'storage' / 'media'
IMAGES_DIR = MEDIA_DIR / 'images'
THUMBS_DIR = MEDIA_DIR / 'thumbnails'
REPO_DIR = MEDIA_DIR / 'repository'


def _has_image_or_thumb(filename: str) -> bool:
    name = Path(filename).name
    return bool(list(IMAGES_DIR.rglob(name))) or (THUMBS_DIR / name).exists()


def test_no_static_url_for_media_in_templates_or_display() -> None:
    """Prevent url_for('static', filename='images/...') regressions."""
    forbidden_pattern = re.compile(
        r"url_for\(\s*['\"]static['\"]\s*,\s*filename\s*=\s*['\"]"
        r"(?:images|thumbnails|repository|videos|books)/"
    )
    violations: list[str] = []

    files_to_scan = (
        list(TEMPLATES_DIR.rglob('*.html'))
        + list(DISPLAY_DIR.rglob('*.py'))
    )
    for file_path in files_to_scan:
        content = file_path.read_text(encoding='utf-8')
        for line_no, line in enumerate(content.splitlines(), start=1):
            if forbidden_pattern.search(line):  # pragma: no cover
                rel = file_path.relative_to(ROOT_DIR)
                violations.append(f"{rel}:{line_no}: {line.strip()}")

    assert not violations, (
        "Media files in storage/media/ must use "
        "url_for('main.serve_media', ...) instead of url_for('static', ...):\n"
        + "\n".join(violations)
    )


def _check_project_assets(
        key: str, proj: dict[str, Any], missing: list[str]) -> None:
    icon = proj.get('icon')
    if icon and not _has_image_or_thumb(icon):  # pragma: no cover
        missing.append(f"Project '{key}' icon: {icon}")
    for group in ('funded_by', 'host_institutes'):
        for inst in proj.get(group) or []:
            if isinstance(inst, dict) and inst.get('logo'):
                if not (IMAGES_DIR / 'institutes' / inst['logo']).exists():
                    missing.append(  # pragma: no cover
                        f"Project '{key}' {group} logo: {inst['logo']}")
    for img in proj.get('images') or []:
        src = img.get('src')
        if src:
            full = IMAGES_DIR / 'projects' / proj['acronym'] / src
            if not full.exists():  # pragma: no cover
                missing.append(f"Project '{key}' gallery image: {full}")
    results = proj.get('results') or {}
    if isinstance(results, dict):
        for link in results.get('icons') or []:
            if isinstance(link, dict) and link.get('file'):
                if not (REPO_DIR / link['file']).exists():  # pragma: no cover
                    missing.append(
                        f"Project '{key}' result file: {link['file']}")


def _check_events_and_categories(missing: list[str]) -> None:
    for key, val in category_images.items():
        src = val.get('src')
        if src and not (IMAGES_DIR / src).exists():  # pragma: no cover
            missing.append(f"Category image '{key}': {src}")

    for ev in event_list:
        icon = ev.get('icon')
        if icon and not _has_image_or_thumb(icon):  # pragma: no cover
            missing.append(f"Event '{ev.get('id')}' icon: {icon}")
        for att in ev.get('attachment', []):
            path_str = att.get('path', '').lstrip('/')
            if path_str.startswith('repository/'):
                rel = path_str[len('repository/'):]
                if not (REPO_DIR / rel).exists():  # pragma: no cover
                    missing.append(
                        f"Event '{ev.get('id')}' attachment: {path_str}")


def _check_histgeo_and_publications(missing: list[str]) -> None:
    for lid, lec in lectures.items():
        for pres in lec.get('presenters', []):
            portrait = pres.get('portrait')
            if (portrait
                    and not _has_image_or_thumb(portrait)):  # pragma: no cover
                missing.append(f"Lecture {lid} portrait: {portrait}")

    for vnum in volumes:
        if not (IMAGES_DIR / f"vol-{vnum}.png").exists():  # pragma: no cover
            missing.append(f"HistGeo volume {vnum} cover")

    for date_key, nlist in newsletters.items():
        for nitem in nlist:
            url = nitem.get('url', '')
            if '/repository/' in url:  # pragma: no cover
                rel = url.split('/repository/', 1)[1]
                if not (REPO_DIR / rel).exists():
                    missing.append(f"Newsletter {date_key} file: {url}")

    for idx, item in enumerate(list(literatures) + list(presentations)):
        dl = item.get('download')
        if dl and not (REPO_DIR / dl).exists():  # pragma: no cover
            missing.append(f"Publication/Presentation #{idx} download: {dl}")


def test_all_data_dictionary_assets_exist() -> None:
    """Verify every icon, image, logo, and PDF in mop/data/ exists on disk."""
    missing: list[str] = []
    _check_events_and_categories(missing)
    for key, proj in project_data.items():
        _check_project_assets(key, proj, missing)
    _check_histgeo_and_publications(missing)

    with app.app_context():
        for tvol in get_volume_metadata():
            icon_name = f"{tvol['key']}_register_icon.jpg"
            if not _has_image_or_thumb(icon_name):  # pragma: no cover
                missing.append(f"TIB volume '{tvol['key']}' icon: {icon_name}")

    assert not missing, "Missing media assets:\n" + "\n".join(missing)


def test_css_urls_resolve_to_existing_files() -> None:
    """Ensure all url(...) paths in mop/static/css/*.css exist."""
    css_url_pattern = re.compile(r"url\(['\"]?([^'\")\s]+)['\"]?\)")
    missing: list[str] = []

    for css_file in (STATIC_DIR / 'css').glob('*.css'):
        text = css_file.read_text(encoding='utf-8', errors='ignore')
        for match in css_url_pattern.finditer(text):
            url = match.group(1).split('?')[0].split('#')[0]
            if url.startswith(('data:', 'http://', 'https://')):
                continue
            if url.startswith('/media/'):
                target = MEDIA_DIR / url[len('/media/'):]
            elif url.startswith('/static/'):  # pragma: no cover
                target = STATIC_DIR / url[len('/static/'):]
            else:
                target = (css_file.parent / url).resolve()
            if not target.exists():  # pragma: no cover
                missing.append(f"{css_file.name}: {url} -> {target}")

    assert not missing, "Broken CSS url() paths:\n" + "\n".join(missing)


def _verify_local_url(
        url: str, route: str, client: Any, errors: list[str]) -> None:
    has_node_modules = (STATIC_DIR / 'node_modules').exists()
    if url.startswith('/static/'):
        rel = url[len('/static/'):]
        if rel.startswith('node_modules/') and not has_node_modules:
            return  # pragma: no cover
        if not (STATIC_DIR / rel).exists():  # pragma: no cover
            errors.append(
                f"Page {route} references {url} missing from mop/static/")
    elif url.startswith('/media/'):
        m_resp = client.get(url)
        if m_resp.status_code != 200:  # pragma: no cover
            errors.append(
                f"Page {route} references {url} -> HTTP {m_resp.status_code}")
        m_resp.close()


def test_rendered_pages_static_and_media_parity(client: Any) -> None:
    """Verify rendered pages have valid /static/ and /media/ references."""
    routes = [
        '/',
        '/events',
        '/projects',
        '/histgeo',
        '/literature',
        '/imprint',
        '/tib',
        '/tib/register',
        *[f'/projects/{key}' for key in project_data],
        *[f'/histgeo/{lid}' for lid in lectures],
    ]
    attr_pattern = re.compile(r'(?:src|href|poster)=["\']([^"\']+)["\']')
    checked_urls: set[str] = set()
    errors: list[str] = []

    for route in routes:
        resp = client.get(route, follow_redirects=True)
        if resp.status_code != 200:  # pragma: no cover
            errors.append(f"Route {route} returned HTTP {resp.status_code}")
            continue
        html = resp.get_data(as_text=True)
        for match in attr_pattern.finditer(html):
            url = match.group(1).split('?')[0].split('#')[0]
            if (not url
                    or url in checked_urls
                    or url.startswith(
                        ('http://', 'https://', 'mailto:',
                         'javascript:', 'data:'))):
                continue
            checked_urls.add(url)
            _verify_local_url(url, route, client, errors)

    assert not errors, (
        "Static/Media parity errors detected:\n" + "\n".join(errors)
    )
