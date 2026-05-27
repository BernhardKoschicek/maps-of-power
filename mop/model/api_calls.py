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


@cache.memoize()
def get_view_class(
        parameter: str,
        params: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
    url = f"{app.config['API_PATH']}/view_class/{parameter}"
    if '?' in parameter:
        # Legacy support: if the parameter is a full query string
        # like 'actor?limit=1'
        url = f"{app.config['API_PATH']}/view_class/{parameter}"
        return requests.get(
            url, proxies=get_proxies(), timeout=30).json()['results']

    return requests.get(
        url, params=params, proxies=get_proxies(),
        timeout=30).json()['results']


@cache.memoize()
def system_class_results(parameter: str) -> list[dict[str, Any]]:
    url = f"{app.config['API_PATH']}/system_class/"
    return requests.get(
        f"{url}{parameter}", proxies=get_proxies(),
        timeout=30).json()['results']


@cache.memoize()
def get_typed_entities_all_results(id_: int) -> list[dict[str, Any]]:
    url = f"{app.config['API_PATH']}/type_entities_all/"
    return requests.get(
        f"{url}{id_}", proxies=get_proxies(), timeout=30).json()['results']


@cache.cached(key_prefix='type_tree')
def get_type_tree() -> List[TypeTree]:
    url = f"{app.config['API_PATH']}/type_tree/"
    type_tree = requests.get(
        url, proxies=get_proxies(), timeout=30).json()['typeTree']
    return [TypeTree(types) for types in type_tree.values()]


@cache.memoize()
def get_entity_presentation(id_: int) -> dict[str, Any]:
    url = f"{app.config['API_PATH']}/entity_presentation_view/{id_}"
    response = requests.get(url, proxies=get_proxies(), timeout=30)
    if response.status_code == 404:  # pragma: no cover
        raise NotFound(f"Entity with ID {id_} not found in the external API.")
    response.raise_for_status()
    return response.json()


@cache.memoize()
def get_entity(id_: int) -> dict[str, Any]:
    # Deprecated raw entity loader
    url = f"{app.config['API_PATH']}/entity/"
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
    'appellation',
    'type',
    'type_tools',
    'external_reference',
    'reference_system',
    'source',
    'source_translation', ]


@cache.memoize()
def get_ego_network(id_: int, depth: int = 2) -> dict[str, Any]:
    depth_ = max(1, min(5, depth))
    url = f"{app.config['API_PATH']}/ego_network_visualisation/{id_}"
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
        exclude_system_classes: Optional[list[str]] = None) -> dict[str, Any]:
    if exclude_system_classes is None:
        exclude_system_classes = EXCLUDE_SYSTEM_CLASSES
    url = f"{app.config['API_PATH']}/network_visualisation/"
    params: Any = {
        'exclude_system_classes': exclude_system_classes,
        'linked_to_ids': linked_to_ids}
    response = requests.get(
        url, params=params, proxies=get_proxies(), timeout=30)
    response.raise_for_status()
    return response.json()
