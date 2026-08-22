import uuid
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask
from flask.testing import FlaskClient

from mop.model.entity import Entity
from mop.pid import (
    base62_to_uuid, extract_numeric_entity_id, fetch_entity_by_uuid,
    get_backend_api_bases, rewrite_json_urls, uuid_to_base62)


def test_base62_uuid_roundtrip() -> None:
    test_uuids = [
        "00000000-0000-0000-0000-000000000000",
        "ffffffff-ffff-ffff-ffff-ffffffffffff",
        "12345678-1234-5678-1234-567812345678",
        "a3bb189e-8bf9-4888-9912-ace4e6543002",
        "e7c7e6c4-72de-426b-9c76-586b51ff6e87",
        str(uuid.uuid4()),
        str(uuid.uuid4())]

    for u_str in test_uuids:
        b62 = uuid_to_base62(u_str)
        assert b62.isalnum()
        decoded = base62_to_uuid(b62)
        assert decoded == u_str

    # Test with uuid.UUID instance
    u_obj = uuid.uuid4()
    b62 = uuid_to_base62(u_obj)
    assert base62_to_uuid(b62) == str(u_obj)


def test_base62_invalid_inputs() -> None:
    with pytest.raises(TypeError):
        uuid_to_base62(12345)  # type: ignore

    with pytest.raises(ValueError):
        base62_to_uuid("")

    with pytest.raises(ValueError):
        base62_to_uuid("invalid-char!")

    with pytest.raises(ValueError):
        # 128-bit overflow string
        base62_to_uuid("zzzzzzzzzzzzzzzzzzzzzzzzzzzz")


def test_get_backend_api_bases(app: Flask) -> None:
    app.config['MOP_API_PATH'] = 'https://mop.backend/api/'
    app.config['ORTHO_API_PATH'] = 'https://ortho.backend/api/'
    app.config['OPENATLAS_API_BASE'] = 'https://custom.backend/api/'

    bases = get_backend_api_bases()
    assert 'https://mop.backend/api' in bases
    assert 'https://ortho.backend/api' in bases
    assert 'https://custom.backend/api' in bases


def test_rewrite_json_urls() -> None:
    backend_base = "https://mop.backend/api"
    request_domain = "https://maps-of-power.at"

    target_uuid = "a3bb189e-8bf9-4888-9912-ace4e6543002"
    expected_b62 = uuid_to_base62(target_uuid)
    expected_pid_url = f"{request_domain}/id/{expected_b62}"

    data = {
        "@id": f"{backend_base}/uuid/{target_uuid}",
        "url": f"{backend_base}/entity/{target_uuid}",
        "href": f"{backend_base}/{target_uuid}",
        "description": f"See {backend_base}/uuid/{target_uuid} for info.",
        "external_link": "https://en.wikipedia.org/wiki/Constantinople",
        "nested": {
            "link": f"{backend_base}/uuid/{target_uuid}",
            "notes": "Do not touch this text."},
        "items": [
            {"@id": f"{backend_base}/uuid/{target_uuid}"},
            "plain string"]}

    rewritten = rewrite_json_urls(
        data, request_domain, backend_bases=[backend_base])

    assert rewritten["@id"] == expected_pid_url
    assert rewritten["url"] == expected_pid_url
    assert rewritten["href"] == expected_pid_url
    # Verify description is NOT modified (no raw regex over text)
    assert rewritten["description"] == (
        f"See {backend_base}/uuid/{target_uuid} for info.")
    assert rewritten["external_link"] == (
        "https://en.wikipedia.org/wiki/Constantinople")
    assert rewritten["nested"]["link"] == expected_pid_url
    assert rewritten["nested"]["notes"] == "Do not touch this text."
    assert rewritten["items"][0]["@id"] == expected_pid_url
    assert rewritten["items"][1] == "plain string"


def test_extract_numeric_entity_id() -> None:
    assert extract_numeric_entity_id({"id": 42}) == 42
    assert extract_numeric_entity_id(
        {"properties": {"id": 100}}) == 100
    assert extract_numeric_entity_id(
        {"properties": {"@id": "200"}}) == 200

    # Complex Linked Art identified_by with GeoNames and Internal Database ID
    linked_art_data = {
        "identified_by": [
            {
                "type": "Identifier",
                "_label": "GeoNames Identifier",
                "content": "736354",
                "classified_as": [{"_label": "Authority Control Number"}]},
            {
                "type": "Identifier",
                "_label": "TIB 1 DigTIB Reader Identifier",
                "content": "152"},
            {
                "type": "Identifier",
                "_label": "Internal Database ID",
                "content": "124770",
                "classified_as": [
                    {"id": "https://vocab.getty.edu/aat/300417447",
                     "_label": "internal identification"}]}]}
    assert extract_numeric_entity_id(linked_art_data) == 124770

    # Internal id by id URI
    data_by_uri = {
        "identified_by": [
            {
                "id": ("https://openatlas.maps-of-power.at/api/"
                       "generated/internal_id/abc"),
                "type": "Identifier",
                "content": "555"}]}
    assert extract_numeric_entity_id(data_by_uri) == 555

    assert extract_numeric_entity_id({}) is None
    assert extract_numeric_entity_id("not-a-dict") is None  # type: ignore


@patch("mop.pid.requests.get")
def test_fetch_entity_by_uuid(mock_get: MagicMock, app: Flask) -> None:
    app.config['MOP_API_PATH'] = 'https://mop.backend/api/'
    app.config['ORTHO_API_PATH'] = 'https://ortho.backend/api/'

    target_uuid = "a3bb189e-8bf9-4888-9912-ace4e6543002"

    # Scenario 1: First attempt succeeds
    mock_resp_200 = MagicMock()
    mock_resp_200.status_code = 200
    mock_resp_200.json.return_value = {"id": 123, "name": "Success"}
    mock_get.return_value = mock_resp_200

    result = fetch_entity_by_uuid(target_uuid)
    assert result == {"id": 123, "name": "Success"}

    # Scenario 2: 404 on first, 200 on fallback
    mock_resp_404 = MagicMock()
    mock_resp_404.status_code = 404

    mock_get.side_effect = [
        mock_resp_404, mock_resp_404, mock_resp_404,
        mock_resp_200]
    result = fetch_entity_by_uuid(target_uuid)
    assert result == {"id": 123, "name": "Success"}

    # Scenario 3: Exception or all 404
    mock_get.side_effect = Exception("Network timeout")
    result = fetch_entity_by_uuid(target_uuid)
    assert result is None


@patch("mop.pid.fetch_entity_by_uuid")
def test_pid_resolver_json_suffix(
        mock_fetch: MagicMock, client: FlaskClient, app: Flask) -> None:
    target_uuid = "a3bb189e-8bf9-4888-9912-ace4e6543002"
    b62 = uuid_to_base62(target_uuid)
    app.config['MOP_API_PATH'] = 'https://mop.backend/api/'

    mock_fetch.return_value = {
        "@id": f"https://mop.backend/api/uuid/{target_uuid}",
        "_label": "Test Entity",
        "type": "Place"}

    response = client.get(f"/id/{b62}.json")
    assert response.status_code == 200
    assert response.content_type == "application/json"
    data = response.get_json()
    assert data["_label"] == "Test Entity"
    assert data["@id"] == f"http://localhost/id/{b62}"
    assert f"<http://localhost/id/{b62}>; rel=\"canonical\"" in (
        response.headers.get("Link", ""))


@patch("mop.pid.fetch_entity_by_uuid")
def test_pid_resolver_accept_json_ld(
        mock_fetch: MagicMock, client: FlaskClient, app: Flask) -> None:
    target_uuid = "a3bb189e-8bf9-4888-9912-ace4e6543002"
    b62 = uuid_to_base62(target_uuid)
    app.config['MOP_API_PATH'] = 'https://mop.backend/api/'

    mock_fetch.return_value = {
        "@id": f"https://mop.backend/api/uuid/{target_uuid}",
        "_label": "Test Place"}

    response = client.get(
        f"/id/{b62}", headers={"Accept": "application/ld+json"})
    assert response.status_code == 200
    assert response.content_type == "application/ld+json"
    data = response.get_json()
    assert data["_label"] == "Test Place"


@patch("mop.pid.fetch_entity_by_uuid")
def test_pid_resolver_html_redirect(
        mock_fetch: MagicMock, client: FlaskClient) -> None:
    target_uuid = "a3bb189e-8bf9-4888-9912-ace4e6543002"
    b62 = uuid_to_base62(target_uuid)

    mock_fetch.return_value = {
        "id": 999,
        "_label": "Test Entity With Numeric ID"}

    response = client.get(
        f"/id/{b62}", headers={"Accept": "text/html"})
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/entity/999")


@patch("mop.pid.fetch_entity_by_uuid")
def test_pid_resolver_html_landing(
        mock_fetch: MagicMock, client: FlaskClient) -> None:
    target_uuid = "a3bb189e-8bf9-4888-9912-ace4e6543002"
    b62 = uuid_to_base62(target_uuid)

    mock_fetch.return_value = {
        "_label": "Test Entity Without Numeric ID",
        "description": "A very important place."}

    response = client.get(
        f"/id/{b62}", headers={"Accept": "text/html"})
    assert response.status_code == 200
    assert b"Test Entity Without Numeric ID" in response.data
    assert b"Persistent Identifier (PID)" in response.data


def test_pid_resolver_invalid_base62(client: FlaskClient) -> None:
    response = client.get("/id/invalid-id!.json")
    assert response.status_code == 400
    assert response.get_json()["code"] == 400

    response_html = client.get(
        "/id/invalid-id!", headers={"Accept": "text/html"})
    assert response_html.status_code == 400


@patch("mop.pid.fetch_entity_by_uuid")
def test_pid_resolver_not_found(
        mock_fetch: MagicMock, client: FlaskClient) -> None:
    target_uuid = "a3bb189e-8bf9-4888-9912-ace4e6543002"
    b62 = uuid_to_base62(target_uuid)
    mock_fetch.return_value = None

    response = client.get(f"/id/{b62}.json")
    assert response.status_code == 404
    assert response.get_json()["code"] == 404

    response_html = client.get(
        f"/id/{b62}", headers={"Accept": "text/html"})
    assert response_html.status_code == 404


def test_entity_pid_properties(app: Flask) -> None:
    target_uuid = "a3bb189e-8bf9-4888-9912-ace4e6543002"
    e = Entity(id_="123", name="Test Entity", description="Desc",
               system_class="Place", uuid=target_uuid)

    expected_b62 = uuid_to_base62(target_uuid)
    assert e.base62_id == expected_b62

    with app.test_request_context(base_url="https://maps-of-power.at/"):
        assert e.pid_url == f"https://maps-of-power.at/id/{expected_b62}"

    # Entity without uuid
    e_no_uuid = Entity(id_="456", name="No UUID", description="Desc",
                       system_class="Place")
    assert e_no_uuid.base62_id is None
    assert e_no_uuid.pid_url is None
