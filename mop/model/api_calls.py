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
    url = f"{app.config['API_PATH']}/entities_linked_to_entity/"
    show_ = ''.join([f'&show={value}' for value in show] if show else '')
    return requests.get(
        f"{url}{id_}?limit=0{show_}",
        proxies=get_proxies(),
        timeout=30).json()['results']


def get_entity(id_: int) -> dict[str, Any]:
    url = f"{app.config['API_PATH']}/entity/"
    return requests.get(
        f"{url}{id_}",
        proxies=get_proxies(),
        timeout=30).json()['features'][0]


def api_call(url: str) -> dict[str, Any]:
    return requests.get(
        url,
        proxies=get_proxies(),
        timeout=30).json()['features'][0]
