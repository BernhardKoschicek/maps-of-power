import re
from typing import Any, List, Dict, Optional
from flask import url_for
from mop.model.entity import Entity, Relation


def build_target_link(
        rel: Relation, project: Optional[str] = None,
        view: Optional[str] = None) -> str:
    try:
        url = url_for(
            'entity_project_view',
            id_=rel.relation_to_id,
            project=project,
            view=view
        )
    except Exception:
        # Fallback URL if flask application context is missing or url_for fails
        url = (
            f"/projects/{project}/explore/{view}/{rel.relation_to_id}"
            if project and view else f"/entity/{rel.relation_to_id}")

    link_html = (
        f'<a href="{url}" class="link-primary fw-bold text-decoration-none">'
        f'{rel.label}</a>')

    # Format and append date range if available
    if rel.begin or rel.end:
        date_str = ""
        if rel.begin and rel.end and rel.begin == rel.end:
            date_str = rel.begin
        else:
            begin_part = rel.begin or ""
            end_part = rel.end or ""
            if begin_part and end_part:
                date_str = f"{begin_part} – {end_part}"
            else:
                date_str = begin_part or end_part
        if date_str:
            link_html += f' <span class="text-muted small">({date_str})</span>'

    return link_html


def join_targets(target_links: List[str]) -> str:
    if not target_links:
        return ""
    if len(target_links) == 1:
        return target_links[0]
    if len(target_links) == 2:
        return f"{target_links[0]} and {target_links[1]}"
    return ", ".join(target_links[:-1]) + f", and {target_links[-1]}"


def parse_relationship_term(type_str: str, inverse: bool) -> str:
    if not type_str:
        return "Related to"

    # 1. Parse parenthesized inverse e.g. "ParentOf(ChildOf)"
    type_str = type_str.strip()
    match = re.match(r'^([^(]+)\(([^)]+)\)$', type_str)
    if match:
        non_inverse = match.group(1).strip()
        inverse_val = match.group(2).strip()
        term = inverse_val if inverse else non_inverse
    else:
        term = type_str

    # 2. Split camelcase e.g. "ParentOf" -> "Parent Of"
    term = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', term)

    # 3. Clean up casing (capitalize first letter of each word except
    # common particles/prepositions)
    words = term.split()
    if not words:
        return "Related to"

    prepositions = {
        "of", "to", "in", "for", "with", "by", "at", "on", "from", "and",
        "or", "in-law", "or-niece", "niece"}

    formatted_words = []
    for i, word in enumerate(words):
        lower_word = word.lower()
        if i > 0 and (lower_word in prepositions or "-" in lower_word):
            formatted_words.append(lower_word)
        else:
            if "-" in word:
                parts = word.split("-")
                formatted_parts = [parts[0].capitalize()] + [
                    p.lower() for p in parts[1:]]
                formatted_words.append("-".join(formatted_parts))
            else:
                formatted_words.append(word.capitalize())

    formatted_term = " ".join(formatted_words)

    # 4. Append "of" if it doesn't end with "of" or "to"
    if (not formatted_term.lower().endswith("of") and
            not formatted_term.lower().endswith("to")):
        formatted_term = f"{formatted_term} of"

    return formatted_term


class NarrativePropertyConfig:
    def __init__(
        self,
        label: str,
        templates: Dict[str, str],
        default_template: str = "Connected via {property_label} to {targets}.",
        icon: str = "bi-chat-left-quote"
    ):
        self.label = label
        self.templates = templates
        self.default_template = default_template
        self.icon = icon

    def get_template(self, system_class: str) -> str:
        key = system_class.lower()
        return self.templates.get(key, self.default_template)

    def generate_narratives(
        self,
        source_entity: Entity,
        relations: List[Relation],
        project: Optional[str] = None,
        view: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        target_links = []
        for rel in relations:
            link_html = build_target_link(rel, project, view)
            target_links.append(link_html)

        if not target_links:
            return []

        targets_str = join_targets(target_links)
        template = self.get_template(source_entity.system_class)
        narrative_text = template.format(
            targets=targets_str,
            property_label=self.label
        )
        return [{"text": narrative_text, "icon": self.icon}]


class ActorRelationshipConfig(NarrativePropertyConfig):
    def generate_narratives(
        self,
        source_entity: Entity,
        relations: List[Relation],
        project: Optional[str] = None,
        view: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        # Group relations by their resolved relationship term
        # (e.g. "Child of", "Spouse of")
        term_groups: Dict[str, List[Relation]] = {}

        for rel in relations:
            type_str = rel.type or ""
            term = parse_relationship_term(type_str, rel.inverse)
            if term not in term_groups:
                term_groups[term] = []
            term_groups[term].append(rel)

        narratives = []
        # Sort terms alphabetically for stable layout presentation
        for term in sorted(term_groups.keys()):
            rel_list = term_groups[term]
            target_links = []
            for rel in rel_list:
                link_html = build_target_link(rel, project, view)
                target_links.append(link_html)

            targets_str = join_targets(target_links)
            narrative_text = f"{term} {targets_str}."
            narratives.append({"text": narrative_text, "icon": self.icon})

        return narratives


# Central registry mapping ontology properties to their respective config
# models
NARRATIVE_CONFIGS = {
    "crm:P74_has_current_or_former_residence": NarrativePropertyConfig(
        label="residence/home",
        templates={
            "place": "Served as the residence/home for {targets}.",
            "person": "Had their residence/home in {targets}.",
            "group": "Had their residence/home in {targets}."
        },
        icon="bi-geo-alt"
    ),
    "crm:P74i_is_current_or_former_residence_of": NarrativePropertyConfig(
        label="residence/home",
        templates={
            "place": "Served as the residence/home for {targets}.",
            "person": "Had their residence/home in {targets}.",
            "group": "Had their residence/home in {targets}."
        },
        icon="bi-geo-alt"
    ),
    "crm:OA7_has_relationship_to": ActorRelationshipConfig(
        label="relationship",
        templates={},
        icon="bi-people"
    ),
    "crm:OA7i_has_relationship_to": ActorRelationshipConfig(
        label="relationship",
        templates={},
        icon="bi-people"
    ),
    "crm:P2_has_type": NarrativePropertyConfig(
        label="classification",
        templates={
            "place": (
                "Categorized as or forms part of the project {targets}."),
            "person": (
                "Classified under the category or case study of {targets}."),
            "group": (
                "Classified under the category or case study of {targets}."),
            "artifact": (
                "Classified under the category or case study of {targets}."),
            "event": "Associated with the project or case study {targets}.",
            "activity": "Associated with the project or case study {targets}.",
            "move": "Associated with the project or case study {targets}.",
            "acquisition": (
                "Associated with the project or case study {targets}.")
        },
        default_template="Categorized under the type/project {targets}.",
        icon="bi-bookmark-star"
    ),
    "crm:P2i_is_type_of": NarrativePropertyConfig(
        label="type categorization",
        templates={},
        default_template=(
            "Serves as the type/project classification for {targets}."),
        icon="bi-bookmark-star"
    ),
    "crm:P11_had_participant": NarrativePropertyConfig(
        label="participant",
        templates={
            "activity": (
                "Brought together the historical participants {targets}."),
            "event": (
                "Brought together the historical participants {targets}."),
            "acquisition": "Brought together the participants {targets}.",
            "move": "Brought together the participants {targets}."
        },
        default_template="Had participant {targets}.",
        icon="bi-person-check"
    ),
    "crm:P11i_participated_in": NarrativePropertyConfig(
        label="participation",
        templates={
            "person": (
                "Participated in the historical event or activity of "
                "{targets}."),
            "group": (
                "Participated as a collective in the event or activity of "
                "{targets}.")
        },
        default_template="Participated in {targets}.",
        icon="bi-person-check"
    ),
    "crm:P14_carried_out_by": NarrativePropertyConfig(
        label="executor",
        templates={
            "activity": (
                "Was carried out or sponsored by the historical actor(s) "
                "{targets}."),
            "event": "Was carried out by the historical actor(s) {targets}.",
            "acquisition": (
                "Was carried out by the historical actor(s) {targets}."),
            "move": "Was carried out by the historical actor(s) {targets}.",
            "production": "Was produced by the historical actor(s) {targets}.",
            "creation": "Was created by the historical actor(s) {targets}."
        },
        default_template="Was carried out by {targets}.",
        icon="bi-briefcase"
    ),
    "crm:P14i_performed": NarrativePropertyConfig(
        label="performed action",
        templates={
            "person": "Sponsored or carried out the execution of {targets}.",
            "group": "Sponsored or carried out the execution of {targets}."
        },
        default_template="Successfully performed or executed {targets}.",
        icon="bi-briefcase"
    ),
    "crm:P22_transferred_title_to": NarrativePropertyConfig(
        label="title transfer",
        templates={
            "activity": "Transferred legal title or rank to {targets}.",
            "acquisition": "Transferred legal title or rank to {targets}."
        },
        default_template="Transferred title to {targets}.",
        icon="bi-award"
    ),
    "crm:P22i_acquired_title_through": NarrativePropertyConfig(
        label="acquired title",
        templates={
            "person": (
                "Acquired their noble title or administrative rank through "
                "the transaction of {targets}."),
            "group": "Acquired title or rank through {targets}."
        },
        default_template="Acquired title through {targets}.",
        icon="bi-award"
    ),
    "crm:P23_transferred_title_from": NarrativePropertyConfig(
        label="title relinquishment",
        templates={
            "activity": "Transferred legal title or property from {targets}.",
            "acquisition": (
                "Transferred legal title or property from {targets}.")
        },
        default_template="Transferred title from {targets}.",
        icon="bi-shield-x"
    ),
    "crm:P23i_surrendered_title_through": NarrativePropertyConfig(
        label="surrendered title",
        templates={
            "person": (
                "Surrendered or relinquished their title/estate through the "
                "transaction of {targets}."),
            "group": "Surrendered title or property through {targets}."
        },
        default_template="Relinquished rights through {targets}.",
        icon="bi-shield-x"
    ),
    "crm:P24_transferred_title_of": NarrativePropertyConfig(
        label="ownership transfer",
        templates={
            "activity": "Transferred ownership or donation of {targets}.",
            "acquisition": "Transferred ownership or donation of {targets}."
        },
        default_template="Transferred ownership/donation of {targets}.",
        icon="bi-gift"
    ),
    "crm:P24i_changed_ownership_through": NarrativePropertyConfig(
        label="ownership change",
        templates={
            "place": (
                "Passed into new ownership or was formally donated through "
                "{targets}."),
            "artifact": (
                "Passed into new ownership or was formally donated through "
                "{targets}.")
        },
        default_template="Changed ownership or was donated through {targets}.",
        icon="bi-gift"
    ),
    "crm:P25_moved": NarrativePropertyConfig(
        label="moved object",
        templates={
            "move": (
                "Involved the spatial transfer and relocation of {targets}.")
        },
        default_template="Moved {targets}.",
        icon="bi-arrows-move"
    ),
    "crm:P25i_moved_by": NarrativePropertyConfig(
        label="relocated by",
        templates={
            "artifact": (
                "Was moved or transported during the historical event of "
                "{targets}.")
        },
        default_template="Was relocated or moved by {targets}.",
        icon="bi-arrows-move"
    ),
    "crm:P9_consists_of": NarrativePropertyConfig(
        label="composition",
        templates={
            "activity": "Consists of the sub-events of {targets}.",
            "event": "Consists of the sub-events of {targets}."
        },
        default_template="Consists of {targets}.",
        icon="bi-diagram-3"
    ),
    "crm:P9i_forms_part_of": NarrativePropertyConfig(
        label="constituent part",
        templates={
            "activity": (
                "Forms a constituent part of the larger historical episode of "
                "{targets}."),
            "event": (
                "Forms a constituent part of the larger historical episode of "
                "{targets}.")
        },
        default_template="Forms part of {targets}.",
        icon="bi-diagram-3"
    )
}


class NarrativeGenerator:
    @staticmethod
    def generate(
            entity: Entity, project: Optional[str] = None,
            view: Optional[str] = None) -> List[Dict[str, Any]]:
        if not entity.relations:
            return []

        # We will group relations by the matched narrative property key
        groups: Dict[str, List[Relation]] = {}

        for _, rel_list in entity.relations.items():
            for rel in rel_list:
                rel_properties = getattr(rel, "properties", [])
                for prop in rel_properties:
                    if prop in NARRATIVE_CONFIGS:
                        if prop not in groups:
                            groups[prop] = []
                        groups[prop].append(rel)

        narratives = []

        # Process each property group using its configured
        # NarrativePropertyConfig generator
        for prop_uri in sorted(groups.keys()):
            config = NARRATIVE_CONFIGS[prop_uri]
            rel_list = groups[prop_uri]
            prop_narratives = config.generate_narratives(
                entity, rel_list, project=project, view=view)
            narratives.extend(prop_narratives)

        return narratives
