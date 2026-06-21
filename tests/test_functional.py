from flask.testing import FlaskClient


def test_about_route(client: FlaskClient) -> None:
    response = client.get('/')
    assert response.status_code == 200
    assert b'Maps of Power' in response.data


def test_events_route(client: FlaskClient) -> None:
    response = client.get('/events')
    assert response.status_code == 200


def test_histgeo_index_route(client: FlaskClient) -> None:
    response = client.get('/histgeo')
    assert response.status_code == 200


def test_histgeo_detail_route(client: FlaskClient) -> None:
    response = client.get('/histgeo/1')
    assert response.status_code == 200


def test_imprint_route(client: FlaskClient) -> None:
    response = client.get('/imprint')
    assert response.status_code == 200


def test_set_language_route(client: FlaskClient) -> None:
    response = client.get(
        '/language=de',
        headers={'Referer': '/'},
    )
    assert response.status_code == 302
    with client.session_transaction() as sess:
        assert sess['language'] == 'de'


def test_literature_route(client: FlaskClient) -> None:
    response = client.get('/literature')
    assert response.status_code == 200


def test_projects_index_route(client: FlaskClient) -> None:
    response = client.get('/projects')
    assert response.status_code == 200


def test_projects_detail_route(client: FlaskClient) -> None:
    response = client.get('/projects/vlachs')
    assert response.status_code == 200


def test_project_explore_table_route(client: FlaskClient) -> None:
    response = client.get('/projects/vlachs/explore/actor')
    assert response.status_code == 200


def test_entity_view_route(client: FlaskClient) -> None:
    response = client.get('/entity/124486')
    assert response.status_code == 200


def test_entity_view_route_with_translations(client: FlaskClient) -> None:
    response = client.get('/entity/880')
    assert response.status_code == 200
    assert b'Treskavac 2 cyrillic' in response.data
    assert b'Treskavac 2 latin' in response.data
    assert (
        b'href="#trans-2772-pane"' in response.data
        or b'data-bs-target="#trans-2772-pane"' in response.data)
    assert (
        b'href="#trans-881-pane"' in response.data
        or b'data-bs-target="#trans-881-pane"' in response.data)


def test_project_entity_view_route(client: FlaskClient) -> None:
    response = client.get('/projects/tib_balkan/explore/place/124486')
    assert response.status_code == 200


def test_software_route(client: FlaskClient) -> None:
    response = client.get('/software')
    assert response.status_code == 200


def test_iiif_viewer_route(client: FlaskClient) -> None:
    response = client.get('/iiif_viewer?manifest=http://example.org/manifest')
    assert response.status_code == 200


def test_atlas_redirect_route(client: FlaskClient) -> None:
    response = client.get('/atlas')
    assert response.status_code == 302
    assert response.location == 'https://atlas.maps-of-power.at/'


def test_frontend_redirect_route(client: FlaskClient) -> None:
    response = client.get('/frontend')
    assert response.status_code == 302
    assert response.location == 'https://atlas.maps-of-power.at/'


def test_network_api_route(client: FlaskClient) -> None:
    response = client.get('/api/network/237?depth=1')
    assert response.status_code == 200
    assert response.json is not None
    assert 'results' in response.json


def test_locale_selector_from_session(client: FlaskClient) -> None:
    with client.session_transaction() as sess:
        sess['language'] = 'de'
    response = client.get('/')
    assert response.status_code == 200


def test_api_project_network_routes(client: FlaskClient) -> None:
    # Test specific project network route
    response = client.get('/api/network/project/holdura')
    assert response.status_code == 200
    assert response.json is not None
    assert 'results' in response.json

    # Test aggregate 'all' project network route
    response_all = client.get('/api/network/project/all')
    assert response_all.status_code == 200
    assert response_all.json is not None
    assert 'results' in response_all.json

    # Test invalid project network route
    response_invalid = client.get('/api/network/project/invalid_project')
    assert response_invalid.status_code == 404


def test_project_api_routing() -> None:
    from mop.views import get_project_api_path
    # 'rhr' project has 'api': 'ortho'
    assert get_project_api_path('rhr') == 'https://openatlas.orthodoxes-europa.at/api/'
    # 'holdura' project does not have 'api': 'ortho'
    assert get_project_api_path('holdura') == 'https://openatlas.maps-of-power.at/api/'
    # None or invalid project acronyms should default to MOP
    assert get_project_api_path(None) == 'https://openatlas.maps-of-power.at/api/'
    assert get_project_api_path('invalid') == 'https://openatlas.maps-of-power.at/api/'
