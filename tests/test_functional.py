from unittest.mock import patch

from flask.testing import FlaskClient


def test_about_route(client: FlaskClient) -> None:
    response = client.get('/')
    assert response.status_code == 200
    assert b'Maps of Power' in response.data


def test_health_route(client: FlaskClient) -> None:
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {'status': 'ok', 'version': '0.1.0'}


def test_events_route(client: FlaskClient) -> None:
    response = client.get('/events')
    assert response.status_code == 200
    assert b'byzantine_congress_250826' in response.data


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
    assert response.headers['Location'].endswith('/')
    with client.session_transaction() as sess:
        assert sess['language'] == 'de'

    # Reject external open redirect and unsupported language codes
    ext_resp = client.get(
        '/language=invalid_lang',
        headers={'Referer': 'https://evil.example.com/phishing'},
    )
    assert ext_resp.status_code == 302
    assert 'evil.example.com' not in ext_resp.headers['Location']
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
    trusted = 'https://openatlas.maps-of-power.at/iiif_manifest/123'
    response = client.get(f'/iiif_viewer?manifest={trusted}')
    assert response.status_code == 200
    assert (
        b'"loadedManifest": '
        b'"https://openatlas.maps-of-power.at/iiif_manifest/123?url='
        in response.data)

    for bad in ('', 'http://evil.example.org/manifest', 'javascript:alert(1)'):
        bad_resp = client.get(f'/iiif_viewer?manifest={bad}')
        assert bad_resp.status_code == 400
    assert client.get('/iiif_viewer').status_code == 400


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
    ortho_url = 'https://openatlas.orthodoxes-europa.at/api/'
    mop_url = 'https://openatlas.maps-of-power.at/api/'
    # 'rhr' project has 'api': 'ortho'
    assert get_project_api_path('rhr') == ortho_url
    # 'holdura' project does not have 'api': 'ortho'
    assert get_project_api_path('holdura') == mop_url
    # None or invalid project acronyms should default to MOP
    assert get_project_api_path(None) == mop_url
    assert get_project_api_path('invalid') == mop_url


def test_youtube_iframe_helpers(client: FlaskClient) -> None:
    from mop.util import youtube_iframe, youtube_iframe_with_logos

    # Simple iframe without logos
    simple_html = youtube_iframe('https://www.youtube.com/embed/test')
    assert 'iframe' in simple_html
    assert 'https://www.youtube.com/embed/test' in simple_html
    assert 'col-md-8' in simple_html

    # Iframe with single and both logos
    with_both = youtube_iframe_with_logos(
        'https://www.youtube.com/embed/test',
        left_logo='/static/images/left.png',
        right_logo='/static/images/right.png',
    )
    assert '/static/images/left.png' in with_both
    assert '/static/images/right.png' in with_both
    assert 'order-md-1' in with_both
    assert 'order-md-2' in with_both
    assert 'order-md-3' in with_both

    # Test holdura project page rendering
    response = client.get('/projects/holdura')
    assert response.status_code == 200
    assert b'apox_schwarz.png' in response.data
    assert b'ram_schwarz.png' in response.data
    assert b'NV4TT4QnFNI' in response.data


def test_array_split() -> None:
    from mop.util import array_split
    assert array_split([], 4) == [[], [], [], []]
    chunks = array_split(list(range(10)), 4)
    assert chunks == [[0, 1, 2], [3, 4, 5], [6, 7], [8, 9]]


def test_entity_view_null_view_class_routes(client: FlaskClient) -> None:
    with patch('mop.model.entity.get_entity_presentation') as mock_pres:
        mock_pres.return_value = {
            "id": 999991,
            "systemClass": "object_location",
            "viewClass": None,
            "title": "Mock Object Location"}
        response = client.get('/entity/999991')
        assert response.status_code == 200
        assert b'Mock Object Location' in response.data

        proj_response = client.get('/projects/idcew/explore/place/999991')
        assert proj_response.status_code == 200
        assert b'/projects/idcew/explore/place' in proj_response.data

        mock_pres.return_value = {
            "id": 999992,
            "systemClass": "type_tools",
            "viewClass": None,
            "title": "Mock Type Tool"}
        response_tool = client.get('/entity/999992')
        assert response_tool.status_code == 200
        assert b'Mock Type Tool' in response_tool.data

        proj_tool = client.get('/projects/idcew/explore/place/999992')
        assert proj_tool.status_code == 200
        assert b'Type tools' in proj_tool.data


def test_security_headers_and_explore_validation(client: FlaskClient) -> None:
    health = client.get('/health')
    assert health.status_code == 200
    assert 'Content-Security-Policy' in health.headers
    assert health.headers.get('Referrer-Policy') == (
        'strict-origin-when-cross-origin')
    assert 'Permissions-Policy' in health.headers
    assert health.headers.get('X-XSS-Protection') == '0'

    with patch('mop.views._fetch_table_rows',
               return_value={'results': [], 'pagination': {}}) as mock_rows:
        resp = client.get(
            '/api/explore/vlachs/actor?page=-5&sort=DROP&column=HACK')
        assert resp.status_code == 200
        mock_rows.assert_called_once()
        _, _, page, sort, col, search = mock_rows.call_args[0]
        assert page == 1
        assert sort == 'asc'
        assert col == 'name'
        assert search == ''

    with patch('mop.views.get_oa_by_view_class',
               side_effect=RuntimeError('upstream down')):
        err_resp = client.get('/projects/vlachs/explore/actor')
        assert err_resp.status_code == 503


def test_iiif_viewer_rejects_spoofed_host_header(client: FlaskClient) -> None:
    resp = client.get(
        '/iiif_viewer?manifest=https://evil.example/manifest.json',
        headers={'Host': 'evil.example'})
    assert resp.status_code == 400


def test_set_language_rejects_backslash_and_spoofed_host(
        client: FlaskClient) -> None:
    resp_bs = client.get(
        '/language=en', headers={'Referer': '/\\evil.example'})
    assert resp_bs.status_code == 302
    assert 'evil.example' not in resp_bs.headers['Location']

    resp_host = client.get(
        '/language=en',
        headers={
            'Host': 'evil.example',
            'Referer': 'https://evil.example/phish'})
    assert resp_host.status_code == 302
    assert resp_host.headers['Location'] == '/phish'


def test_static_blocks_package_json_and_csp_hardened(
        client: FlaskClient) -> None:
    assert client.get('/static/package.json').status_code == 404
    assert client.get('/static/package-lock.json').status_code == 404
    health = client.get('/health')
    csp = health.headers.get('Content-Security-Policy', '')
    assert "default-src 'self'" in csp
    assert 'script-src' in csp


def test_network_api_clamps_depth_before_cache(client: FlaskClient) -> None:
    with patch(
            'mop.views.get_ego_network',
            return_value={'results': []}) as mock_net:
        resp = client.get('/api/network/237?depth=99')
        assert resp.status_code == 200
        mock_net.assert_called_once()
        assert mock_net.call_args[0] == (237, 5)


def test_entity_view_sanitizes_links_and_popovers(
        client: FlaskClient) -> None:
    with patch('mop.model.entity.get_entity_presentation') as mock_pres:
        mock_pres.return_value = {
            "id": 999993,
            "uuid": "a3bb189e-8bf9-4888-9912-ace4e6543002",
            "systemClass": "place",
            "viewClass": "place",
            "title": "Hardened Entity",
            "externalReferenceSystems": [
                {
                    "referenceURL": "javascript:alert(1)",
                    "referenceSystem": "BadSys"},
                {
                    "referenceURL": "https://example.org/ref",
                    "referenceSystem": "GoodSys"}],
            "references": [
                {
                    "id": 42,
                    "systemClass": "bibliography",
                    "title": "<script>alert(1)</script>",
                    "citation": "<b>bad</b>"}],
            "types": [
                {
                    "id": 7,
                    "title": "TypeA",
                    "isStandard": True,
                    "descriptions": "<img src=x>",
                    "typeHierarchy": []}]}
        resp = client.get('/entity/999993')
        assert resp.status_code == 200
        assert b'javascript:alert(1)' not in resp.data
        assert b'https://example.org/ref' in resp.data
        assert b'data-popover-kind="reference"' in resp.data
        assert b'data-popover-kind="type"' in resp.data
        assert b'onclick=' not in resp.data
