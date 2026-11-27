from http.cookiejar import DefaultCookiePolicy
import json
import re
import threading
from typing import Any, List, Optional

import requests
from requests.adapters import HTTPAdapter
from werkzeug.exceptions import NotFound

from mop.extensions import cache, get_app_config
from mop.model.typetree import TypeTree

_session_local = threading.local()
DEFAULT_HTTP_TIMEOUT: tuple[int, int] = (4, 20)


def _freeze_value(val: Any) -> Any:
    if isinstance(val, list):
        return tuple(_freeze_value(v) for v in val)
    if isinstance(val, dict):
        return tuple((k, _freeze_value(v)) for k, v in sorted(val.items()))
    return val


def _freeze_params(
        params: Optional[dict[str, Any]]) -> tuple[tuple[str, Any], ...]:
    if not params:
        return ()
    return tuple((k, _freeze_value(v)) for k, v in sorted(params.items()))


def _thaw_value(val: Any) -> Any:
    if isinstance(val, tuple):
        return [_thaw_value(v) for v in val]
    return val


def get_http_session() -> requests.Session:
    """Return a thread-local pooled requests Session without cookies."""
    session: Optional[requests.Session] = getattr(
        _session_local, 'session', None)
    if session is None:
        session = requests.Session()
        session.cookies.set_policy(DefaultCookiePolicy(allowed_domains=[]))
        adapter = HTTPAdapter(pool_connections=10, pool_maxsize=20)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        _session_local.session = session
    return session


def get_proxies() -> dict[str, str] | None:
    proxy = get_app_config('API_PROXY')
    if not proxy:
        return None
    return {  # pragma: no cover
        "http": proxy,
        "https": proxy}


def _get_api_path(api_path: Optional[str] = None) -> str:
    if api_path:
        return api_path
    return get_app_config('MOP_API_PATH', '')



def _fetch_json(
        url: str,
        params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    response = get_http_session().get(
        url,
        params=params,
        proxies=get_proxies(),
        timeout=DEFAULT_HTTP_TIMEOUT)
    if response.status_code == 404:  # pragma: no cover
        raise NotFound(f"Resource not found: {url}")
    response.raise_for_status()
    data = response.json()
    return data if isinstance(data, dict) else {}


@cache.memoize()
def _get_view_class_cached(
        parameter: str,
        frozen_params: tuple[tuple[str, Any], ...],
        api_path: Optional[str] = None) -> list[dict[str, Any]]:
    base = _get_api_path(api_path).rstrip('/')
    url = f"{base}/view_class/{parameter}"
    if '?' in parameter:
        # Legacy support: if the parameter is a full query string
        # like 'actor?limit=1'
        return _fetch_json(url).get('results', [])

    params = (
        {k: _thaw_value(v) for k, v in frozen_params}
        if frozen_params else None)
    return _fetch_json(url, params=params).get('results', [])


def get_view_class(
        parameter: str,
        params: Optional[dict[str, Any]] = None,
        api_path: Optional[str] = None) -> list[dict[str, Any]]:
    return _get_view_class_cached(
        parameter, _freeze_params(params), api_path=api_path)


@cache.memoize()
def system_class_results(
        parameter: str,
        api_path: Optional[str] = None) -> list[dict[str, Any]]:
    base = _get_api_path(api_path).rstrip('/')
    url = f"{base}/system_class/{parameter}"
    return _fetch_json(url).get('results', [])


@cache.memoize()
def get_typed_entities_all_results(
        id_: int,
        api_path: Optional[str] = None) -> list[dict[str, Any]]:
    base = _get_api_path(api_path).rstrip('/')
    url = f"{base}/type_entities_all/{id_}"
    return _fetch_json(url).get('results', [])


@cache.memoize()
def get_type_tree(api_path: Optional[str] = None) -> List[TypeTree]:
    base = _get_api_path(api_path).rstrip('/')
    url = f"{base}/type_tree/"
    type_tree = _fetch_json(url).get('typeTree', {})
    return [TypeTree(types) for types in type_tree.values()]


@cache.memoize()
def get_entity_presentation(
        id_: int,
        api_path: Optional[str] = None) -> dict[str, Any]:
    base = _get_api_path(api_path).rstrip('/')
    url = f"{base}/entity_presentation_view/{id_}"
    response = get_http_session().get(
        url, proxies=get_proxies(), timeout=DEFAULT_HTTP_TIMEOUT)
    if response.status_code == 404:  # pragma: no cover
        raise NotFound(f"Entity with ID {id_} not found in the external API.")
    response.raise_for_status()
    return response.json()


@cache.memoize()
def get_entity(id_: int, api_path: Optional[str] = None) -> dict[str, Any]:
    # Deprecated raw entity loader
    base = _get_api_path(api_path).rstrip('/')
    url = f"{base}/entity/"
    response = get_http_session().get(
        f"{url}{id_}", proxies=get_proxies(), timeout=DEFAULT_HTTP_TIMEOUT)
    if response.status_code == 404:  # pragma: no cover
        raise NotFound(f"Entity with ID {id_} not found in the external API.")
    response.raise_for_status()
    data = response.json()
    if not data.get('features'):  # pragma: no cover
        raise NotFound(f"Entity with ID {id_} has no features.")
    return data['features'][0]


EXCLUDE_SYSTEM_CLASSES = [
    'administrative_unit',
    'alias',
    'type',
    'type_tools',
    'external_reference',
    'reference_system',
    'source',
    'text', ]


@cache.memoize()
def get_ego_network(
        id_: int,
        depth: int = 2,
        api_path: Optional[str] = None) -> dict[str, Any]:
    depth_ = max(1, min(5, depth))
    base = _get_api_path(api_path).rstrip('/')
    url = f"{base}/ego_network_visualisation/{id_}"
    params: Any = {
        'depth': depth_,
        'exclude_system_classes': EXCLUDE_SYSTEM_CLASSES}
    response = get_http_session().get(
        url,
        params=params,
        proxies=get_proxies(),
        timeout=DEFAULT_HTTP_TIMEOUT)
    if response.status_code == 404:  # pragma: no cover
        raise NotFound(f"Ego network not found for ID {id_}.")
    response.raise_for_status()
    return response.json()


@cache.memoize()
def _get_network_visualisation_cached(
        linked_to_ids: tuple[int, ...],
        exclude_system_classes: tuple[str, ...],
        api_path: Optional[str] = None) -> dict[str, Any]:
    base = _get_api_path(api_path).rstrip('/')
    url = f"{base}/network_visualisation/"
    params: Any = {
        'exclude_system_classes': list(exclude_system_classes),
        'linked_to_ids': list(linked_to_ids)}
    response = get_http_session().get(
        url,
        params=params,
        proxies=get_proxies(),
        timeout=DEFAULT_HTTP_TIMEOUT)
    response.raise_for_status()
    return response.json()


def get_network_visualisation(
        linked_to_ids: list[int],
        exclude_system_classes: Optional[list[str]] = None,
        api_path: Optional[str] = None) -> dict[str, Any]:
    norm_ids = tuple(sorted(set(linked_to_ids)))
    norm_excludes = tuple(
        exclude_system_classes
        if exclude_system_classes is not None else EXCLUDE_SYSTEM_CLASSES)
    return _get_network_visualisation_cached(
        norm_ids, norm_excludes, api_path=api_path)


# pylint: disable=too-many-arguments, too-many-positional-arguments
# pylint: disable=too-many-locals
def fetch_table_rows_uncached(
        view: str, oa_ids: tuple[str, ...], page: int, sort: str, column: str,
        search: str, api_path: Optional[str] = None) -> dict[str, Any]:
    """Proxy call to OpenAtlas /table_rows/."""
    base = _get_api_path(api_path).rstrip('/')
    url = f"{base}/0.4/table_rows/"
    params: dict[str, Any] = {
        'view_classes': view,
        'sort': sort,
        'column': column,
        'page': page,
        'table_columns': [
            'begin', 'class', 'description', 'end', 'name', 'type'],
        'type_id': list(oa_ids), }
    if search:
        params['search'] = json.dumps({
            'entityName': [{
                'operator': 'like',
                'values': [search],
                'logicalOperator': 'and'}]})
    response = get_http_session().get(
        url,
        params=params,
        proxies=get_proxies(),
        timeout=DEFAULT_HTTP_TIMEOUT)
    response.raise_for_status()
    data = response.json()
    rows = []
    for row in data.get('results', []):
        if not isinstance(row, list) or len(row) < 6:
            continue
        m = re.search(r'\bid="(\d+)"', str(row[0]))
        if not m:
            continue
        rows.append({
            'id': int(m.group(1)),
            'begin': row[1] or '',
            'class_': row[2] or '',
            'description': row[3] or '',
            'end': row[4] or '',
            'name': row[5] or '',
            'type': row[6] if len(row) > 6 else '', })
    return {'results': rows, 'pagination': data.get('pagination', {})}


# pylint: disable=too-many-arguments, too-many-positional-arguments
@cache.memoize(timeout=3600)
def fetch_table_rows(
        view: str, oa_ids: tuple[str, ...], page: int, sort: str, column: str,
        search: str, api_path: Optional[str] = None) -> dict[str, Any]:
    """Cached proxy call to OpenAtlas /table_rows/ for non-search queries."""
    return fetch_table_rows_uncached(
        view, oa_ids, page, sort, column, search, api_path=api_path)


@cache.memoize(timeout=3600)
def fetch_table_rows_count(
        view: str, oa_ids: tuple[str, ...],
        api_path: Optional[str] = None) -> int:
    """Fetch total row count for an explore table view."""
    base = _get_api_path(api_path).rstrip('/')
    url = f"{base}/0.4/table_rows/"
    params: dict[str, Any] = {
        'view_classes': view,
        'count': 'true',
        'type_id': list(oa_ids), }
    response = get_http_session().get(
        url,
        params=params,
        proxies=get_proxies(),
        timeout=DEFAULT_HTTP_TIMEOUT)
    response.raise_for_status()
    try:
        return int(response.text.strip())
    except ValueError:
        return 0
