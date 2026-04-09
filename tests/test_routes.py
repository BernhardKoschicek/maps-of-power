from unittest.mock import patch, MagicMock
import pytest

# Mocking Entity and API calls to avoid external requests during route testing
@pytest.fixture(autouse=True)
def mock_api_calls():
    with patch('mop.model.api_calls.requests.get') as mock_get:
        # Mock response for a generic API call
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'results': [],
            'features': [{
                '@id': 'http://example.org/entity/123',
                'properties': {'title': 'Test Entity'},
                'descriptions': [{'value': 'Test Description'}],
                'systemClass': 'person',
                'types': [],
                'names': [],
                'relations': [],
                'depictions': [],
                'links': [],
                'geometry': None
            }],
            'typeTree': {}
        }
        mock_get.return_value = mock_response
        yield mock_get

def test_about_route(client):
    resp = client.get("/")
    assert resp.status_code == 200

def test_events_route(client):
    resp = client.get("/events")
    assert resp.status_code == 200

def test_histgeo_index_route(client):
    resp = client.get("/histgeo")
    assert resp.status_code == 200

def test_histgeo_detail_route(client):
    # Testing with ID 1 which exists in mop/data/histgeo.py
    resp = client.get("/histgeo/1")
    assert resp.status_code == 200

def test_imprint_route(client):
    resp = client.get("/imprint")
    assert resp.status_code == 200

def test_set_language_route(client):
    # referrer is needed for redirect
    resp = client.get("/language=de", environ_base={'HTTP_REFERER': '/'})
    assert resp.status_code == 302
    with client.session_transaction() as sess:
        assert sess['language'] == 'de'

def test_literature_route(client):
    resp = client.get("/literature")
    assert resp.status_code == 200

def test_projects_index_route(client):
    resp = client.get("/projects")
    assert resp.status_code == 200

def test_projects_detail_route(client):
    # 'rhr' is a valid project key in mop/data/projects/projects.py
    resp = client.get("/projects/rhr")
    assert resp.status_code == 200

def test_project_explore_table_route(client):
    # Valid project 'rhr' and valid view 'actor'
    resp = client.get("/projects/rhr/explore/actor")
    assert resp.status_code == 200

def test_entity_view_route(client):
    resp = client.get("/entity/123")
    assert resp.status_code == 200

def test_project_entity_view_route(client):
    resp = client.get("/projects/rhr/explore/actor/123")
    assert resp.status_code == 200

def test_software_route(client):
    resp = client.get("/software")
    assert resp.status_code == 200

def test_iiif_viewer_route(client):
    resp = client.get("/iiif_viewer?manifest=http://example.org/manifest")
    assert resp.status_code == 200

def test_atlas_redirect_route(client):
    resp = client.get("/atlas")
    assert resp.status_code == 302
    assert resp.location == "https://atlas.maps-of-power.at/"

def test_frontend_redirect_route(client):
    resp = client.get("/frontend")
    assert resp.status_code == 302
    assert resp.location == "https://atlas.maps-of-power.at/"
