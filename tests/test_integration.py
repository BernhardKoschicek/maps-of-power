from mop.model.api_calls import (
    get_type_tree,
    get_entity,
    get_view_class,
    system_class_results,
    get_typed_entities_all_results,
    get_ego_network,
)
from mop.model.entity import Entity
from mop.model.util import (
    uc_first,
    split_date_string,
    format_date,
    flatten_list_and_remove_duplicates,
)
from mop.util import (
    get_dates_formatted,
    get_table_dates_formatted,
    get_dict_entries_by_category,
    get_types_sorted,
)


def test_api_get_type_tree() -> None:
    trees = get_type_tree()
    assert isinstance(trees, list)
    if trees:
        assert hasattr(trees[0], 'id')


def test_api_get_entity() -> None:
    data = get_entity(124486)
    assert isinstance(data, dict)
    assert '@id' in data
    assert 'properties' in data


def test_api_get_view_class() -> None:
    results = get_view_class('actor?limit=1')
    assert isinstance(results, list)


def test_api_system_class_results() -> None:
    results = system_class_results('person?limit=1')
    assert isinstance(results, list)


def test_api_get_typed_entities_all_results() -> None:
    results = get_typed_entities_all_results(124486)
    assert isinstance(results, list)





def test_api_get_ego_network() -> None:
    results = get_ego_network(237, 1)
    assert isinstance(results, dict)
    assert 'results' in results


def test_api_get_entity_presentation() -> None:
    from mop.model.api_calls import get_entity_presentation
    data = get_entity_presentation(124486)
    assert isinstance(data, dict)
    assert 'id' in data
    assert 'systemClass' in data
    assert 'relations' in data



def test_entity_model() -> None:
    entity = Entity.get_entity_from_oa(124486)
    assert isinstance(entity, Entity)
    assert entity.id_ == '124486'
    assert entity.name is not None
    assert entity.system_class is not None


def test_model_util_uc_first() -> None:
    assert uc_first('hello') == 'Hello'
    assert uc_first('') == ''


def test_model_util_split_date_string() -> None:
    assert split_date_string('2026-05-23T12:00:00') == '23.05.2026'
    assert split_date_string(None) == ''


def test_model_util_format_date() -> None:
    assert format_date('01.01.2026', '31.12.2026') == '2026'
    assert format_date('1.1.2026', '31.12.2026') == '2026'
    assert format_date('01.1.2026', '31.12.2026') == '2026'
    assert format_date('1.01.2026', '31.12.2026') == '2026'
    assert format_date('01.01.1219', '31.12.1220') == '1219 – 1220'
    assert format_date('01.01.2026', '31.12.2027') == '2026 – 2027'
    assert format_date('01.01.2026', None) == '01.01.2026'


def test_model_util_flatten_list_and_remove_duplicates() -> None:
    input_list = [[1, 2], [2, 3], [3, 4]]
    assert flatten_list_and_remove_duplicates(input_list) == [1, 2, 3, 4]


def test_util_get_dates_formatted() -> None:
    assert get_dates_formatted(2026, 5, 23) == '23.05.2026'


def test_util_get_table_dates_formatted() -> None:
    assert get_table_dates_formatted(2026, 5, 23) == '2026/05/23'


def test_util_get_dict_entries_by_category() -> None:
    data = [
        {'category': ['rhr', 'other']},
        {'category': ['vlachs']},
    ]
    assert get_dict_entries_by_category('rhr', data) == [{'category': ['rhr', 'other']}]
    assert get_dict_entries_by_category(['vlachs'], data) == [{'category': ['vlachs']}]


def test_util_get_types_sorted() -> None:
    assert get_types_sorted([]) is None
    from mop.model.types import Types
    t = Types(
        label='Test Label',
        hierarchy='Root > Sub',
        value='some-value',
        unit='kg',
        description='desc',
        identifier='123',
        root='Root')
    res = get_types_sorted([t])
    assert res == {'Root': [t]}


def test_explore_get_oa_by_view_class() -> None:
    from mop.model.explore import get_oa_by_view_class
    # Test invalid view
    assert get_oa_by_view_class('invalid_view', '123') == []
    # Test list of IDs
    res = get_oa_by_view_class('actor', ['124486'])
    assert isinstance(res, list)


def test_types_constructor_with_dict() -> None:
    from mop.model.types import Types
    data = {
        'label': 'Test Label',
        'hierarchy': 'Root > Sub',
        'value': 'some-value',
        'unit': 'kg',
        'descriptions': 'desc',
        'identifier': 'http://example.org/types/123'}
    t = Types(data=data)
    assert t.label == 'Test Label'
    assert t.hierarchy == 'Root > Sub'
    assert t.value == 'some-value'
    assert t.unit == 'kg'
    assert t.description == 'desc'
    assert t.identifier == '123'
    assert t.root == 'Root'


def test_model_util_format_date_fallbacks() -> None:
    # Test len != 3
    assert (format_date('01.01', '31.12.2026') ==
            'between 01.01 and 31.12.2026')
    # Test ValueError
    assert (format_date('ab.cd.efgh', '31.12.2026') ==
            'between ab.cd.efgh and 31.12.2026')


def test_display_image_gallery() -> None:
    from mop import app
    from mop.display.image import image_gallery
    images = {
        'img1': {
            'src': 'test.jpg',
            'caption': 'Caption 1',
            'citation': 'Citation 1',
            'description': 'Description 1'},
        'img2': {
            'src': 'test2.jpg',
            'caption': 'Caption 2',
            'citation': 'Citation 2',
            'description': ''}}
    with app.test_request_context():
        result = image_gallery(images)
    assert 'Description 1' in result
    assert 'img2' in result
