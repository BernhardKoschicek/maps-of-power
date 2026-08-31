"""Unit and integration tests for TIB register and reader functionality."""

# pylint: disable=redefined-outer-name
import pytest
from mop import app
from mop.data.events import event_list
from mop.data.literature import literatures
from mop.data.projects.projects import project_data
from mop.model.tib_db import (
    get_reader_pages, get_volume_metadata, normalize_search_term,
    search_toponyms)


@pytest.fixture
def client():
    """Create Flask test client."""
    app.config['TESTING'] = True
    with app.test_client() as test_client:
        yield test_client


def test_normalize_search_term():
    """Test diacritic folding and Greek homoglyph conversion."""
    assert normalize_search_term('Αchelōοs') == 'acheloos'
    assert normalize_search_term('Acheloos') == 'acheloos'
    assert normalize_search_term('Lēmnos') == 'lemnos'
    assert normalize_search_term('Chōra') == 'chora'
    assert normalize_search_term('Sōtēr Christos') == 'soter christos'
    assert normalize_search_term('') == ''


def test_search_toponyms_all():
    """Test querying all toponyms without search term."""
    result = search_toponyms(limit=25, offset=0)
    assert result['total'] == 70191
    assert len(result['results']) == 25
    first = result['results'][0]
    assert 'name' in first
    assert 'pages' in first
    assert 'pages_display' in first


def test_search_toponyms_by_volume():
    """Test filtering toponyms by volume ID."""
    res_tib1 = search_toponyms(volume_id=1, limit=50)
    assert res_tib1['total'] == 2209

    res_tib2 = search_toponyms(volume_id=2, limit=50)
    assert res_tib2['total'] == 2199


def test_search_greek_and_diacritic_tolerance():
    """Test that searching with or without accents finds Greek names."""
    res1 = search_toponyms(query='acheloos')
    assert res1['total'] > 0
    names1 = [r['name'] for r in res1['results']]
    assert any('Achel' in n or 'Αchel' in n for n in names1)

    res2 = search_toponyms(query='lemnos')
    assert res2['total'] > 0
    names2 = [r['name'] for r in res2['results']]
    assert any('Lēmnos' in n or 'Lemnos' in n for n in names2)


def test_citation_commentary_formatting():
    """Test that commentary citations are formatted as '52 (A. 75)'."""
    res = search_toponyms(query='Aidepsos', volume_id=1)
    assert res['total'] > 0
    item = res['results'][0]
    assert '52 (A. 75)' in item['pages_display']


def test_get_volume_metadata():
    """Test volume metadata structure and page counts."""
    volumes = get_volume_metadata()
    assert len(volumes) == 18
    tib1 = next(v for v in volumes if v['key'] == 'tib1')
    assert tib1['published'] is True
    assert tib1['has_reader'] is True
    assert tib1['pages'] == 315
    assert tib1['toponym_count'] == 2209


def test_get_reader_pages():
    """Test page retrieval for book reader."""
    pages = get_reader_pages('tib1')
    assert len(pages) == 315
    assert pages[0]['page_num'] == 1
    pages13 = get_reader_pages('tib13')
    assert len(pages13) == 1367
    assert pages13[0]['filename'] == 'TIB13_Seite_0001.jpg'
    assert pages13[577]['filename'] == 'TIB13_Seite_0578.jpg'

    assert not get_reader_pages('tib14')
    assert not get_reader_pages('nonexistent')


def test_tib_overview_route(client):
    """Test GET /tib overview route."""
    response = client.get('/tib')
    assert response.status_code == 200
    assert b'Tabula Imperii Byzantini' in response.data
    assert b'TIB 1 Hellas and Thessaly' in response.data


def test_tib_register_route(client):
    """Test GET /tib/register routes."""
    res_all = client.get('/tib/register')
    assert res_all.status_code == 200
    assert b'TIB Toponym Register' in res_all.data

    res_vol = client.get('/tib/register/tib1')
    assert res_vol.status_code == 200
    assert b'TIB 1' in res_vol.data

    res_404 = client.get('/tib/register/invalid_vol')
    assert res_404.status_code == 404


def test_tib_reader_route(client):
    """Test GET /tib/reader/<volume> route."""
    res_reader = client.get('/tib/reader/tib1')
    assert res_reader.status_code == 200
    assert b'fullPageReader' in res_reader.data

    # Volume without scans returns 404
    res_no_reader = client.get('/tib/reader/tib14')
    assert res_no_reader.status_code == 404


def test_api_tib_search(client):
    """Test /api/tib/search endpoint."""
    res = client.get('/api/tib/search?q=Lemnos&limit=10')
    assert res.status_code == 200
    data = res.get_json()
    assert data['total'] > 0
    assert len(data['results']) <= 10
    assert data['query'] == 'Lemnos'


def test_api_tib_reader_pages(client):
    """Test /api/tib/reader/<volume>/pages endpoint."""
    res = client.get('/api/tib/reader/tib1/pages')
    assert res.status_code == 200
    data = res.get_json()
    assert data['total_pages'] == 315
    assert len(data['pages']) == 315

    res_404 = client.get('/api/tib/reader/tib14/pages')
    assert res_404.status_code == 404


def test_tib_project_definition(client):
    """Test TIB project metadata and project routes."""
    assert 'tib' in project_data
    tib = project_data['tib']
    assert tib['acronym'] == 'tib'
    assert 'Tabula Imperii Byzantini' in str(tib['title'])
    assert tib['begin'] == '01.01.1966'
    assert str(tib['end']) == 'ongoing'
    assert len(tib['description']) == 4
    assert len(tib['images']) == 4
    assert len(tib['employees']) == 12
    assert 'Peter Soustal' in tib['employees']
    assert 'Klaus Belke' in tib['employees']
    assert 'Friedrich Hild' in tib['employees']
    assert 'Despoina Ariantzi' in tib['employees']

    # Test /projects overview includes tib
    res_projects = client.get('/projects')
    assert res_projects.status_code == 200
    assert b'data-acronym="tib"' in res_projects.data

    # Test /projects/tib detail page
    res_details = client.get('/projects/tib')
    assert res_details.status_code == 200
    assert b'Tabula Imperii Byzantini (TIB)' in res_details.data
    assert b'Hellas und Thessalia' in res_details.data
    assert b'tab-pub-volumes' in res_details.data
    assert b'tab-pub-vtib' in res_details.data
    assert b'tab-pub-histgeo' in res_details.data
    assert b'tab-pub-monographs' in res_details.data
    assert b'tab-pub-articles' in res_details.data


def test_tib_events_migrated(client):
    """Test that TIB outreach activities were migrated to events."""
    assert len(event_list) == 28
    event_ids = {e['id'] for e in event_list}
    expected_ids = [
        'les_ciutats_mediterranies_151222',
        'tib11_promotion_141122',
        'histgeo_leipzig_101122',
        'aieb_roundtable_220822',
        'hypotheses_post_150822',
        'tib11_release_260722',
        'imc_leeds_060722',
        'seminar_koeln_230622',
        'lange_nacht_200522',
        'global_eurasia_120522',
        'lead_seals_190422',
        'seminar_series_010422']
    for eid in expected_ids:
        assert eid in event_ids

    # Test /events page
    res = client.get('/events')
    assert res.status_code == 200
    assert b'lead_seals_190422' in res.data
    assert b'tib11_promotion_141122' in res.data


def test_tib_publications_migrated(client):
    """Test that TIB publications were migrated to literature."""
    assert len(literatures) >= 200
    tib_lits = [l for l in literatures if 'tib' in l.get('category', [])]
    assert len(tib_lits) == 198

    # Check the 5 categories are present
    types = {l.get('type') for l in tib_lits}
    assert types == {
        'Volumes', 'VTIB', 'HistGeo', 'Monographs', 'Articles'}

    # Check that TIB volumes have register links
    tib_vols = [
        l for l in tib_lits
        if '/tib/register/' in l.get('external_link', '')]
    assert len(tib_vols) == 14

    # Test /literature page
    res = client.get('/literature')
    assert res.status_code == 200
    assert b'data-filter="tib"' in res.data
    assert b'Hellas und Thessalia' in res.data
    assert b'data-type-filter="volumes"' in res.data
    assert b'data-type-filter="vtib"' in res.data
    assert b'data-type-filter="histgeo"' in res.data
