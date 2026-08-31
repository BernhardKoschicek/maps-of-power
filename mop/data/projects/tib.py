"""Tabula Imperii Byzantini (TIB) project definition."""

from flask_babel import lazy_gettext as _

from mop.data.institutes import institutes
from mop.util import get_dates_formatted

images = [
    {
        'src': 'frontmap.png',
        'description': _(
            'Research area of the Tabula Imperii Byzantini across the '
            'Eastern Mediterranean and Balkans'),
        'citation': 'Austrian Academy of Sciences (ÖAW)',
        'category': ['tib']},
    {
        'src': 'tib_regions_hunger.jpg',
        'description': _(
            'Overview map of the TIB regional volume boundaries and zones'),
        'citation': 'Herbert Hunger, ÖAW',
        'category': ['tib']},
    {
        'src': 'euboia_1967.png',
        'description': _(
            'Historical field research and topographical survey in Euboea '
            '(1967)'),
        'citation': 'Johannes Koder',
        'category': ['tib']},
    {
        'src': 'altwege_2014.jpg',
        'description': _(
            'Field research and ancient road surveys in the Balkans (2014)'),
        'citation': 'Mihailo Popović',
        'category': ['tib']}]

project_tib = {
    'acronym': 'tib',
    'title': _('Tabula Imperii Byzantini (TIB)'),
    'website': '/tib',
    'host_institutes': [institutes['abf'], institutes['imafo']],
    'funded_by': [institutes['oeaw'], institutes['uai']],
    'project_number': 'Project 87 (UAI) / ÖAW Long-Term Project',
    'pi': [
        'Herbert Hunger (1966–1996)',
        'Johannes Koder (1996–2016)',
        'Mihailo Popović (2016–)',
        'Andreas Külzer (2016–)'],
    'cooperation': [],
    'employees': [
        'Despoina Ariantzi',
        'Georgia Theochari',
        'Bernhard Koschiček-Krombholz',
        'Dorota Vargová',
        'Vratislav Zervan',
        'Veronika Polloczek',
        'Moisés Hernández Cordero',
        'Elisabeth Charlotte Beer',
        'David Schmid',
        'Klaus Belke',
        'Friedrich Hild',
        'Peter Soustal'],
    'begin': get_dates_formatted(1966, 1, 1),
    'end': _('ongoing'),
    'description': [
        _(
            'Research on the Historical Geography of the Byzantine Empire at '
            'the Austrian Academy of Sciences in Vienna is conducted by '
            'the Tabula Imperii Byzantini (TIB). This renowned long-term '
            'project was accepted by the Union Académique Internationale '
            'in Brussels in 2015 (Project 87), and at the same time included '
            'into the scheme of Long-Term Projects at the Austrian Academy of '
            'Sciences, based on independent international evaluations. The '
            'TIB carries out systematic research in the historical '
            'geography of the Byzantine Empire, from the beginning of the '
            '4th century to the mid-15th century. The overarching aim of the '
            'project is to create a comprehensive historical atlas of the '
            'Byzantine space from Late Antiquity to the Early Modern period.'),
        _(
            'Individual regions are represented on maps on a scale of '
            '1 : 800,000. A separate accompanying volume provides the '
            'results of further research in each region. Each volume contains '
            'detailed introductory chapters on geography and climate, '
            'borders and territorial designations, history, administrative '
            'history, church history and monasticism, traffic routes, economy '
            'and demographic trends. The main part of each volume consists of '
            'an alphabetical catalogue of all toponyms, hydronyms, and '
            'settlements known in Byzantine times. Written sources and '
            'archaeological evidence elucidate the history of individual '
            'places, enriched by systematic on-site field research.'),
        _(
            'Since 1986 new methods have been continuously incorporated into '
            'the scholarly work of the TIB, including studies of '
            'palaeo-climate, settlement theories (e.g. the modified Central '
            'Place Theory), and the regular use of Global Positioning System '
            '(GPS) receivers during field missions. In recent years, Digital '
            'Humanities—particularly Historical Geographic Information '
            'Systems (HGIS), digital gazetteers, and web-based open access '
            'platforms—have further expanded the analysis, spatial modeling, '
            'and digital preservation of research data.'),
        _(
            'Key Project Achievements (1966–ongoing): 14 TIB volumes '
            'published and 5 in active preparation; over 70,000 verified '
            'historical toponyms catalogued; more than 100,000 photographic '
            'records created; 68 field research missions and surveys '
            'accomplished; and over 180 scholarly monographs, series volumes, '
            'and research articles published.')],
    'results': '',
    'icon': 'digtib.png',
    'images': images,
    'videos': [],
    'oaID': [],
    'api': ''}
