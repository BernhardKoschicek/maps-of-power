import json
import re
import uuid
from typing import Any

import requests
from flask import (
    Response, abort, jsonify, redirect, render_template, request, url_for)

from mop import app
from mop.model.api_calls import get_proxies

BASE62_ALPHABET = (
    "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
BASE62_BASE = 62

URL_KEYS = {
    '@id', 'id', 'url', 'href', 'next', 'previous', 'link', 'seeAlso',
    'sameAs', 'target', 'source', 'value'}

UUID_REGEX = re.compile(
    r'([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-'
    r'[0-9a-fA-F]{4}-[0-9a-fA-F]{12})')


def uuid_to_base62(uuid_val: str | uuid.UUID) -> str:
    """Convert a standard UUID string or object into a Base62 string."""
    if isinstance(uuid_val, str):
        u = uuid.UUID(uuid_val.strip())
    elif isinstance(uuid_val, uuid.UUID):
        u = uuid_val
    else:
        raise TypeError("uuid_val must be a string or uuid.UUID instance")

    num = u.int
    if num == 0:
        return BASE62_ALPHABET[0]

    digits: list[str] = []
    while num > 0:
        num, rem = divmod(num, BASE62_BASE)
        digits.append(BASE62_ALPHABET[rem])
    return "".join(reversed(digits))


def base62_to_uuid(base62_str: str) -> str:
    """Convert a Base62 string back into a hyphenated UUID string."""
    if not isinstance(base62_str, str) or not base62_str:
        raise ValueError("Base62 string must be a non-empty string")

    num = 0
    for char in base62_str:
        idx = BASE62_ALPHABET.find(char)
        if idx == -1:
            raise ValueError(f"Invalid character '{char}' in Base62 string")
        num = num * BASE62_BASE + idx

    if num >= (1 << 128):
        raise ValueError("Base62 value out of range for 128-bit UUID")

    return str(uuid.UUID(int=num))


def get_backend_api_bases() -> list[str]:
    """Return a list of configured backend API base URLs."""
    bases: list[str] = []
    mop_base = app.config.get('MOP_API_PATH', '')
    if mop_base:
        bases.append(mop_base.rstrip('/'))

    ortho_base = app.config.get('ORTHO_API_PATH', '')
    if ortho_base and ortho_base.rstrip('/') not in bases:
        bases.append(ortho_base.rstrip('/'))

    custom_base = app.config.get('OPENATLAS_API_BASE', '')
    if custom_base and custom_base.rstrip('/') not in bases:
        bases.append(custom_base.rstrip('/'))

    return bases


def fetch_entity_by_uuid(uuid_str: str) -> dict[str, Any] | None:
    """Fetch entity data from OpenAtlas backend by UUID."""
    bases = get_backend_api_bases()
    proxies = get_proxies()
    headers = {
        'Accept': 'application/ld+json, application/json'}

    for base in bases:
        urls_to_try = [
            f"{base}/uuid/{uuid_str}",
            f"{base}/{uuid_str}",
            f"{base}/entity/{uuid_str}"]
        for url in urls_to_try:
            try:
                response = requests.get(
                    url, headers=headers, proxies=proxies, timeout=30)
                if response.status_code == 200:
                    return response.json()
                if response.status_code == 404:
                    continue
            except Exception as e:
                app.logger.warning("Error fetching %s: %s", url, e)
                continue
    return None


def rewrite_json_urls(
        data: Any,
        request_domain: str,
        backend_bases: list[str] | None = None) -> Any:
    """Recursively rewrite OpenAtlas backend URLs to Frontend PID URLs."""
    if backend_bases is None:
        backend_bases = get_backend_api_bases()

    frontend_pid_base = f"{request_domain.rstrip('/')}/id"

    def _rewrite_string_url(val: str) -> str:
        for base in backend_bases:
            if val.startswith(base) or base in val:
                match = UUID_REGEX.search(val)
                if match:
                    try:
                        b62 = uuid_to_base62(match.group(1))
                        return f"{frontend_pid_base}/{b62}"
                    except Exception:  # pragma: no cover
                        pass
        return val

    if isinstance(data, dict):
        rewritten_dict: dict[str, Any] = {}
        for k, v in data.items():
            if k in URL_KEYS and isinstance(v, str):
                rewritten_dict[k] = _rewrite_string_url(v)
            elif isinstance(v, (dict, list)):
                rewritten_dict[k] = rewrite_json_urls(
                    v, request_domain, backend_bases)
            else:
                rewritten_dict[k] = v
        return rewritten_dict
    if isinstance(data, list):
        return [
            rewrite_json_urls(item, request_domain, backend_bases)
            for item in data]
    return data


def _is_internal_identifier(ident: dict[str, Any]) -> bool:
    """Check if an identified_by entry is an Internal Database ID."""
    label = str(ident.get('_label', '')).lower()
    ident_id = str(ident.get('id', '')).lower()
    if ('internal database id' in label
            or 'internal id' in label
            or '/internal_id/' in ident_id):
        return True

    for cls_obj in ident.get('classified_as', []):
        if isinstance(cls_obj, dict):
            cls_label = str(cls_obj.get('_label', '')).lower()
            cls_id = str(cls_obj.get('id', ''))
            if ('internal identification' in cls_label
                    or '300417447' in cls_id):
                return True
    return False


def extract_numeric_entity_id(data: dict[str, Any]) -> int | None:
    """Extract numeric OpenAtlas entity ID from entity data if present."""
    if not isinstance(data, dict):
        return None

    def _to_int(val: Any) -> int | None:
        if isinstance(val, int):
            return val
        if isinstance(val, str) and val.isdigit():
            return int(val)
        return None

    result = _to_int(data.get('id'))
    if result is not None:
        return result

    identified_by = data.get('identified_by')
    if isinstance(identified_by, list):
        for ident in identified_by:
            if isinstance(ident, dict) and _is_internal_identifier(ident):
                val = _to_int(ident.get('content'))
                if val is not None:
                    return val

    props = data.get('properties')
    if isinstance(props, dict):
        result = _to_int(props.get('id') or props.get('@id'))
        if result is not None:
            return result

    return None


def is_uuid(identifier: str) -> bool:
    """Check if a string is a valid standard or compact UUID."""
    if not isinstance(identifier, str):
        return False
    val = identifier.strip()
    if len(val) not in (32, 36):
        return False
    try:
        uuid_obj = uuid.UUID(val)
        return str(uuid_obj) == val.lower() or uuid_obj.hex == val.lower()
    except (ValueError, AttributeError):
        return False


@app.route('/id/<identifier>', strict_slashes=False)
@app.route(
    '/id/<identifier>.json',
    endpoint='pid_resolver_json',
    strict_slashes=False)
def pid_resolver(
        identifier: str) -> Response | str | tuple[Response, int]:
    """Dual PID endpoint supporting both Base62 strings and raw UUIDs."""
    is_json_route = request.path.endswith('.json')
    if is_json_route and identifier.endswith('.json'):
        raw_id = identifier[:-5]
    else:
        raw_id = identifier

    accept_header = request.headers.get('Accept', '')
    prefers_json = (
        is_json_route
        or request.accept_mimetypes['application/json'] > (
            request.accept_mimetypes['text/html'])
        or request.accept_mimetypes['application/ld+json'] > (
            request.accept_mimetypes['text/html'])
        or 'application/json' in accept_header
        or 'application/ld+json' in accept_header)

    request_domain = request.host_url.rstrip('/')

    if is_uuid(raw_id):
        uuid_obj = uuid.UUID(raw_id.strip())
        uuid_str = str(uuid_obj)
        base62_id = uuid_to_base62(uuid_obj)

        if not prefers_json:
            return redirect(f"{request_domain}/id/{base62_id}", code=301)
    else:
        base62_id = raw_id
        try:
            uuid_str = base62_to_uuid(base62_id)
        except ValueError:
            if prefers_json:
                return jsonify({
                    'error': 'Invalid Base62 identifier',
                    'code': 400}), 400
            abort(400)

    raw_data = fetch_entity_by_uuid(uuid_str)
    if raw_data is None:
        if prefers_json:
            return jsonify({'error': 'Entity not found', 'code': 404}), 404
        abort(404)

    rewritten_data = rewrite_json_urls(raw_data, request_domain)
    citation_link = f"{request_domain}/id/{base62_id}"

    if prefers_json:
        mimetype = (
            'application/ld+json'
            if 'application/ld+json' in accept_header
            else 'application/json')
        response = Response(
            json.dumps(rewritten_data, ensure_ascii=False),
            mimetype=mimetype,
            status=200)
        response.headers['Link'] = f'<{citation_link}>; rel="canonical"'
        return response

    numeric_id = extract_numeric_entity_id(raw_data)
    if numeric_id is not None:
        return redirect(url_for('entity_project_view', id_=numeric_id))

    return render_template(
        'explore/pid_landing.html',
        entity=rewritten_data,
        citation_link=citation_link,
        base62_id=base62_id)
