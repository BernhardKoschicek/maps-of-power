from mop.model.entity import Entity, Relation
from mop.model.narrative import (
    NarrativePropertyConfig, NarrativeGenerator, parse_relationship_term)


def test_parse_relationship_term() -> None:
    # Inverse cases
    assert parse_relationship_term(
        "ParentOf(ChildOf)", inverse=True) == "Child of"
    assert parse_relationship_term(
        "ParentOf(ChildOf)", inverse=False) == "Parent of"

    assert parse_relationship_term(
        "Uncle (Nephew or niece)", inverse=True) == "Nephew or niece of"
    assert parse_relationship_term(
        "Uncle (Nephew or niece)", inverse=False) == "Uncle of"

    # CamelCase conversion
    assert parse_relationship_term(
        "BrotherInLaw", inverse=False) == "Brother in Law of"
    assert parse_relationship_term(
        "Brother-in-law", inverse=False) == "Brother-in-law of"

    # Symmetric cases
    assert parse_relationship_term("Spouse", inverse=False) == "Spouse of"
    assert parse_relationship_term("Sibling", inverse=False) == "Sibling of"


def test_narrative_property_config() -> None:
    config = NarrativePropertyConfig(
        label="test_prop",
        templates={
            "place": "Place template for {targets}.",
            "person": "Person template for {targets}."})
    assert config.get_template("Place") == "Place template for {targets}."
    assert config.get_template("Person") == "Person template for {targets}."
    assert config.get_template("Unknown") == (
        "Connected via {property_label} to {targets}.")


def test_narrative_generator_empty() -> None:
    entity = Entity(
        id_="999",
        name="Test Entity",
        description="",
        system_class="Place",
        relations=None)
    assert not NarrativeGenerator.generate(entity)


def test_narrative_generator_single_relation() -> None:
    rel = Relation(
        relation_to_id="111",
        label="Target Place",
        system_class="Place",
        begin="1300",
        end="1350",
        type="Residence",
        description="",
        geometry=None,
        properties=["crm:P74_has_current_or_former_residence"])
    entity = Entity(
        id_="222",
        name="John Doe",
        description="",
        system_class="Person",
        relations={"places": [rel]})

    narratives = NarrativeGenerator.generate(entity)
    assert len(narratives) == 1
    # Person source templates: "Had their residence/home in {targets}."
    assert "Had their residence/home in" in narratives[0]['text']
    assert 'href="/entity/111"' in narratives[0]['text']
    assert 'Target Place' in narratives[0]['text']
    assert '(1300 – 1350)' in narratives[0]['text']
    assert narratives[0]['icon'] == 'bi-geo-alt'


def test_narrative_generator_grouping() -> None:
    rel1 = Relation(
        relation_to_id="116716",
        label="Anna Palaiologina",
        system_class="Person",
        begin=None,
        end=None,
        type=None,
        description="",
        geometry=None,
        properties=["crm:P74_has_current_or_former_residence"])
    rel2 = Relation(
        relation_to_id="119946",
        label="Palaiologos Ioannes",
        system_class="Person",
        begin="1325",
        end="1326",
        type=None,
        description="",
        geometry=None,
        properties=["crm:P74_has_current_or_former_residence"])

    entity = Entity(
        id_="111840",
        name="Thessalonike",
        description="",
        system_class="Place",
        relations={"actors": [rel1, rel2]})

    narratives = NarrativeGenerator.generate(
        entity, project="macedonia", view="place")
    assert len(narratives) == 1
    # Place source template: "Served as the residence/home for {targets}."
    assert "Served as the residence/home for" in narratives[0]['text']
    assert (
        'href="/projects/macedonia/explore/place/116716"'
        in narratives[0]['text'])
    assert 'Anna Palaiologina' in narratives[0]['text']
    assert (
        'href="/projects/macedonia/explore/place/119946"'
        in narratives[0]['text'])
    assert 'Palaiologos Ioannes' in narratives[0]['text']
    assert '(1325 – 1326)' in narratives[0]['text']
    assert 'Anna Palaiologina</a> and <a' in narratives[0]['text']
    assert narratives[0]['icon'] == 'bi-geo-alt'


def test_actor_to_actor_relationship_narrative() -> None:
    # Related person: Andronikos (116701), who is the parent/inverse of Anna
    # (116716). The relation points from Andronikos to Anna with property
    # crm:OA7i_has_relationship_to (inverse)
    rel = Relation(
        relation_to_id="116701",
        label="Andronikos Angelos Komnenos Dukas Palaiologos",
        system_class="Person",
        begin="1282",
        end="1328",
        type="ParentOf(ChildOf)",
        description="",
        geometry=None,
        properties=["crm:OA7i_has_relationship_to"],
        inverse=True)

    entity = Entity(
        id_="116716",
        name="Anna Palaiologina",
        description="",
        system_class="Person",
        begin="1313",
        end=None,
        relations={"actors": [rel]})

    narratives = NarrativeGenerator.generate(entity)
    assert len(narratives) == 1
    # Since inverse=True, resolves to "Child of"
    assert narratives[0]['text'].startswith("Child of ")
    assert 'Andronikos Angelos Komnenos Dukas Palaiologos' in (
        narratives[0]['text'])
    assert narratives[0]['icon'] == 'bi-people'


def test_new_crm_properties_narrative() -> None:
    # 1. Test crm:P11i_participated_in
    rel_p11 = Relation(
        relation_to_id="8247",
        label="Ethnonym of the Vlachs",
        system_class="Type",
        begin=None,
        end=None,
        type=None,
        description="",
        geometry=None,
        properties=["crm:P11i_participated_in"])
    entity_p11 = Entity(
        id_="123",
        name="Demetrios",
        description="",
        system_class="Person",
        relations={"others": [rel_p11]})
    narratives_p11 = NarrativeGenerator.generate(entity_p11)
    assert len(narratives_p11) == 1
    assert (
        "Participated in the historical event or activity of"
        in narratives_p11[0]['text'])
    assert narratives_p11[0]['icon'] == 'bi-person-check'

    # 2. Test crm:P14i_performed
    rel_p14 = Relation(
        relation_to_id="119588",
        label="Gradac Monastery",
        system_class="Place",
        begin=None,
        end=None,
        type=None,
        description="",
        geometry=None,
        properties=["crm:P14i_performed"])
    entity_p14 = Entity(
        id_="118622",
        name="Jelena Anžujska",
        description="",
        system_class="Person",
        relations={"places": [rel_p14]})
    narratives_p14 = NarrativeGenerator.generate(entity_p14)
    assert len(narratives_p14) == 1
    assert (
        "Sponsored or carried out the execution of"
        in narratives_p14[0]['text'])
    assert narratives_p14[0]['icon'] == 'bi-briefcase'


def test_title_narrative_icon() -> None:
    # Test crm:P22i_acquired_title_through
    rel = Relation(
        relation_to_id="118524",
        label="Acquisition of Title",
        system_class="Activity",
        begin=None,
        end=None,
        type=None,
        description="",
        geometry=None,
        properties=["crm:P22i_acquired_title_through"])
    entity = Entity(
        id_="118511",
        name="Musa",
        description="",
        system_class="Person",
        relations={"activities": [rel]})
    narratives = NarrativeGenerator.generate(entity)
    assert len(narratives) == 1
    assert (
        "Acquired their noble title or administrative rank through the "
        "transaction of" in narratives[0]['text'])
    assert narratives[0]['icon'] == 'bi-award'
