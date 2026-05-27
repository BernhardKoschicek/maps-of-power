from unittest.mock import patch
from flask.testing import FlaskClient
from werkzeug.exceptions import Forbidden, ImATeapot, InternalServerError


def test_404_error_page(client: FlaskClient) -> None:
    response = client.get('/nonexistent-page-path-123')
    assert response.status_code == 404
    assert b'404' in response.data
    assert b'Page Not Found' in response.data


def test_404_bad_lecture(client: FlaskClient) -> None:
    response = client.get('/histgeo/9999')
    assert response.status_code == 404
    assert b'404' in response.data


def test_404_bad_project(client: FlaskClient) -> None:
    response = client.get('/projects/nonexistent-project-slug')
    assert response.status_code == 404
    assert b'404' in response.data


def test_404_bad_explore_view(client: FlaskClient) -> None:
    response = client.get('/projects/vlachs/explore/nonexistent-view')
    assert response.status_code == 404


def test_404_bad_explore_project(client: FlaskClient) -> None:
    response = client.get('/projects/nonexistent-project/explore/actor')
    assert response.status_code == 404


def test_api_error_returns_json(client: FlaskClient) -> None:
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 404
        response = client.get('/api/network/999999')
        assert response.status_code == 404
        assert response.json is not None
        assert 'error' in response.json
        assert response.json['code'] == 404


def test_api_500_error_returns_json(client: FlaskClient) -> None:
    with patch('mop.views.get_ego_network',
               side_effect=ValueError("Test unhandled error")):
        response = client.get('/api/network/123')
        assert response.status_code == 500
        assert response.json is not None
        assert 'error' in response.json


def test_custom_errors_rendering(client: FlaskClient) -> None:
    with patch('mop.views.image_gallery',
               side_effect=Forbidden("Forbidden test")):
        response = client.get('/')
        assert response.status_code == 403
        assert b'403' in response.data
        assert b'Access Denied' in response.data

    with patch('mop.views.image_gallery',
               side_effect=ImATeapot("Teapot test")):
        response = client.get('/')
        assert response.status_code == 418
        assert b'418' in response.data
        assert b"I'm a Teapot" in response.data

    with patch('mop.views.image_gallery',
               side_effect=InternalServerError("Server test")):
        response = client.get('/')
        assert response.status_code == 500
        assert b'500' in response.data
        assert b"Internal Server Error" in response.data
