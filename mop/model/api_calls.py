from typing import Any, List, Optional

import requests

from werkzeug.exceptions import NotFound

from mop import app, cache
from mop.model.typetree import TypeTree

# Proxies are initialized here, but we should ensure app.config is ready.
# In Flask, app.config is populated when the app is created.


def get_proxies() -> dict[str, str] | None:
    proxy = app.config.get('API_PROXY')
    if not proxy:
        return None
    return {  # pragma: no cover
        "http": proxy,
        "https": proxy}


def _get_api_path(api_path: Optional[str] = None) -> str:
    if api_path:
        return api_path
    return app.config.get('MOP_API_PATH', '')


@cache.memoize()
def get_view_class(
        parameter: str,
        params: Optional[dict[str, Any]] = None,
        api_path: Optional[str] = None) -> list[dict[str, Any]]:
    base = _get_api_path(api_path).rstrip('/')
    url = f"{base}/view_class/{parameter}"
    if '?' in parameter:
        # Legacy support: if the parameter is a full query string
        # like 'actor?limit=1'
        url = f"{base}/view_class/{parameter}"
        return requests.get(
            url, proxies=get_proxies(), timeout=30).json()['results']

    return requests.get(
        url, params=params, proxies=get_proxies(),
        timeout=30).json()['results']


@cache.memoize()
def system_class_results(parameter: str, api_path: Optional[str] = None) -> list[dict[str, Any]]:
    base = _get_api_path(api_path).rstrip('/')
    url = f"{base}/system_class/"
    return requests.get(
        f"{url}{parameter}", proxies=get_proxies(),
        timeout=30).json()['results']


@cache.memoize()
def get_typed_entities_all_results(id_: int, api_path: Optional[str] = None) -> list[dict[str, Any]]:
    base = _get_api_path(api_path).rstrip('/')
    url = f"{base}/type_entities_all/"
    return requests.get(
        f"{url}{id_}", proxies=get_proxies(), timeout=30).json()['results']


@cache.memoize()
def get_type_tree(api_path: Optional[str] = None) -> List[TypeTree]:
    base = _get_api_path(api_path).rstrip('/')
    url = f"{base}/type_tree/"
    type_tree = requests.get(
        url, proxies=get_proxies(), timeout=30).json()['typeTree']
    return [TypeTree(types) for types in type_tree.values()]


@cache.memoize()
def get_entity_presentation(id_: int, api_path: Optional[str] = None) -> dict[str, Any]:
    base = _get_api_path(api_path).rstrip('/')
    url = f"{base}/entity_presentation_view/{id_}"
    response = requests.get(url, proxies=get_proxies(), timeout=30)
    if response.status_code == 404:  # pragma: no cover
        raise NotFound(f"Entity with ID {id_} not found in the external API.")
    response.raise_for_status()
    return response.json()


@cache.memoize()
def get_entity(id_: int, api_path: Optional[str] = None) -> dict[str, Any]:
    # Deprecated raw entity loader
    base = _get_api_path(api_path).rstrip('/')
    url = f"{base}/entity/"
    response = requests.get(f"{url}{id_}", proxies=get_proxies(), timeout=30)
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
def get_ego_network(id_: int, depth: int = 2, api_path: Optional[str] = None) -> dict[str, Any]:
    depth_ = max(1, min(5, depth))
    base = _get_api_path(api_path).rstrip('/')
    url = f"{base}/ego_network_visualisation/{id_}"
    params: Any = {
        'depth': depth_,
        'exclude_system_classes': EXCLUDE_SYSTEM_CLASSES}
    response = requests.get(
        url, params=params, proxies=get_proxies(), timeout=30)
    if response.status_code == 404:  # pragma: no cover
        raise NotFound(f"Ego network not found for ID {id_}.")
    response.raise_for_status()
    return response.json()


@cache.memoize()
def get_network_visualisation(
        linked_to_ids: list[int],
        exclude_system_classes: Optional[list[str]] = None,
        api_path: Optional[str] = None) -> dict[str, Any]:
    if exclude_system_classes is None:
        exclude_system_classes = EXCLUDE_SYSTEM_CLASSES
    base = _get_api_path(api_path).rstrip('/')
    url = f"{base}/network_visualisation/"
    params: Any = {
        'exclude_system_classes': exclude_system_classes,
        'linked_to_ids': linked_to_ids}
    response = requests.get(
        url, params=params, proxies=get_proxies(), timeout=30)
    response.raise_for_status()
    return response.json()
