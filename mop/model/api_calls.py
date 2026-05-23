from typing import Any, List, Optional

import requests

from mop import app
from mop.model.typetree import TypeTree

# Proxies are initialized here, but we should ensure app.config is ready.
# In Flask, app.config is populated when the app is created.
def get_proxies() -> dict[str, str] | None:
    proxy = app.config.get('API_PROXY')
    if not proxy:
        return None
    return {
        "http": proxy,
        "https": proxy
    }


def get_view_class(parameter: str) -> list[dict[str, Any]]:
    url = f"{app.config['API_PATH']}/view_class/"
    return requests.get(
        f"{url}{parameter}",
        proxies=get_proxies(),
        timeout=30).json()['results']


def system_class_results(parameter: str) -> list[dict[str, Any]]:
    url = f"{app.config['API_PATH']}/system_class/"
    return requests.get(
        f"{url}{parameter}",
        proxies=get_proxies(),
        timeout=30).json()['results']


def get_typed_entities_all_results(id_: int) -> list[dict[str, Any]]:
    url = f"{app.config['API_PATH']}/type_entities_all/"
    return requests.get(
        f"{url}{id_}",
        proxies=get_proxies(),
        timeout=30).json()['results']


def get_type_tree() -> List[TypeTree]:
    url = f"{app.config['API_PATH']}/type_tree/"
    type_tree = requests.get(
        url,
        proxies=get_proxies(),
        timeout=30).json()['typeTree']
    return [TypeTree(types) for types in type_tree.values()]


def get_entities_linked_to_entity(
        id_: int,
        show: Optional[List[str]] = None) -> list[dict[str, Any]]:
    url = f"{app.config['API_PATH']}/entities_linked_to_entity/{id_}"
    params: dict[str, Any] = {'limit': 0}
    if show:
        params['show'] = show
    response = requests.get(
        url,
        params=params,
        proxies=get_proxies(),
        timeout=30)
    if response.status_code == 404:
        return []
    response.raise_for_status()
    return response.json().get('results', [])


def get_entity(id_: int) -> dict[str, Any]:
    url = f"{app.config['API_PATH']}/entity/"
    response = requests.get(
        f"{url}{id_}",
        proxies=get_proxies(),
        timeout=30)
    if response.status_code == 404:
        from werkzeug.exceptions import NotFound
        raise NotFound(f"Entity with ID {id_} not found in the external API.")
    response.raise_for_status()
    data = response.json()
    if not data.get('features'):
        from werkzeug.exceptions import NotFound
        raise NotFound(f"Entity with ID {id_} has no features.")
    return data['features'][0]


def api_call(url: str) -> dict[str, Any]:
    return requests.get(
        url,
        proxies=get_proxies(),
        timeout=30).json()['features'][0]


def get_ego_network(id_: int, depth: int = 2) -> dict[str, Any]:
    depth_ = max(1, min(10, depth))
    url = f"{app.config['API_PATH']}/ego_network_visualisation/{id_}"
    params = {
        'depth': depth_,
        'exclude_system_classes': [
            'administrative_unit',
            'appellation',
            'type',
            'type_tools']
    }
    response = requests.get(
        url,
        params=params,
        proxies=get_proxies(),
        timeout=30)
    if response.status_code == 404:
        from werkzeug.exceptions import NotFound
        raise NotFound(f"Ego network not found for ID {id_}.")
    response.raise_for_status()
    return response.json()

