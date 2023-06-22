from flask_babel import lazy_gettext as _

from data.institutes import institutes
from util import get_dates_formatted, youtube_iframe

# Todo: Translation keys, not whole text

holdura_description = [
    _('In the current discourse on the integration of the Western Balkans into the European Union the ongoing and envisaged negotiations with the Republics of Montenegro, Serbia and Albania seem to be of remarkable importance in the contemporary media coverage. They comprise a region, which – in a long ago past – played, under the name of Illyricum (Illyrikon), a vital role in the strategic and administrative considerations of the Byzantine Empire.'),
    _('The project builds upon a scholarly cooperation among the academic fields of Byzantine Studies, Medieval History, Historical Geography, Art History, Geography and Geocommunication (GIScience and Cartography) and focuses on two historic regions of “Duklja” and “Raška” being part of the Illyricum. The research hypothesis is that both historic regions constituted a “Sacred Landscape”, which we intend to decipher and to communicate to academia as well as to the interested public with the joint means of Historical Geography, Art History and Geocommunication.'),
    _('Therefore, the project aims at approaching and researching systematically the following three major questions:'),
    _('(1) In which way did the local rulers and the Churches of Rome and Constantinople interact in the regions of “Duklja” and “Raška” from the 11th to the 14th centuries and how is this very interaction mirrored in the distribution pattern of monuments (i.e. the churches and monasteries) in this “Sacred Landscape”?'),
    _('(2) Did the volatile religious affiliation of the local rulers have an impact on the “Sacred Landscape” and where were Latin or Byzantine places of worship transformed or superimposed in the course of time?'),
    _('(3) Can the religious and cultural influence of the Latin and Byzantine (Orthodox) faith be traced through small Latin (i.e. “Western”) as well as Byzantine and Slavic (i.e. “Eastern”) objects of art, not only in the coastal area, but also in its hinterland and in Italy? Both historic regions could prove to be constituting a zone “Beyond East and West”, subject to remarkable processes of transformation from the 11th to the 14th centuries, and have the huge potential to offer data suitable for visualisations as well as formalisation by GIScience. The integration and presentation of the research data (i.e. on the written sources, monuments and objects of art) of the project will be achieved through an already existing database and an online <a hrf="https://data1.geo.univie.ac.at/projects/tibapp">map application</a>.'),
    _('The project is exclusively feasible through a multidisciplinary approach and cooperation between three project partners from Austria (Austrian Academy of Sciences, here Priv.-Doz. Mag. Dr. Mihailo Popović; University of Vienna, here Professor Dr. Karel Kriz) and Germany (Hochschule für Technik, Wirtschaft und Kultur Leipzig, here Professor Dr. Johannes Tripps).Moreover, it is closely connected to the ongoing scholarly work of Mihailo Popović on <a href="/current_status/TIB_17">TIB volume 17 “Nea Epeiros and Praevalis”</a> and on the TIB Sub Project <a href="sub_projects/montenegro">“Cultural Heritage in Times of World War I: The Case of the Austro-Hungarian Relief Map of Montenegro (1916-1918)”</a>.')
],

holdura_results = {
        'text': [
            _('The Team Department of Geography and Regional Research (University of Vienna) has created a customised homepage for our project’s Geocommunication: <a href="https://map.geo.univie.ac.at/bew/" target="_blank">https://map.geo.univie.ac.at/bew/</a>')
        ],
        'list': [],
        'icons': [
            {
                'label': _("relief map of Montenegro"),
                'link': '/static/3dhop/relief.html',  # Todo: hard link
                'file': None,
                'icon': 'bi-image-alt',
            },
            {
                'label': _('browse_tib_balkans_data'),
                'link': '../balkan/digital/explore',  # Todo: hard link
                'file': None,
                'icon': 'bi-stack',
            },
        ]
    },

project_holdura = {
    'acronym': 'holdura',
    'title': _(
        'Beyond East and West: Geocommunicating the Sacred Landscapes '
        'of "Duklja" and "Raška" through Space and Time (11th-14th Cent.)'),
    'funded_by': [institutes['fwf'], institutes['dfg']],
    'project_number': 'I 4330-G',
    'pi': ['Mihailo Popović'],
    'cooperation': [
        'Mag. Markus Breier', 'Lukas Neugebauer, BSc MSc',
        'Florian Korn, BSc MSc', 'Dipl.-Ing. Leonhard Kreil-Brunauer',
        'Ass. Prof. Dr. Branka Vranešević'],
    'employees': [
        'Dorota Vargová', 'Bernhard Koschiček-Krombholz', 'David Schmid'],
    'begin': get_dates_formatted(2020, 3, 1),
    'end': get_dates_formatted(2023, 8, 31),
    'description': holdura_description,
    'icon': 'holdura_icon.jpg',
    'outreach': [],
    'videos': [
        youtube_iframe('https://www.youtube-nocookie.com/embed/Nhdx2OeWkN8')],
    'part': 'balkan',
    'oaID': 117730,
}
