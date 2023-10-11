from flask_babel import lazy_gettext as _

from mop.util import get_table_dates_formatted

presentations = [{
    'presenter': 'Mihailo St. Popović',
    'title': 'Serbian Noblewomen and the Clergy in the Middle Ages: '
             'A Comparison between Mara Branković and Jelena Anžujska '
             'regarding Athonite Monks and Franciscan Friars',
    'conference': 'Workshop „A Special Relationship? Gender on Medieval '
                  'Mount Athos“',
    'location': [_('Oxford')],
    'date': get_table_dates_formatted(2023, 9, 29),
    'external_link': '',
    'download': '',
    'category': ['holdura']
}, {
    'presenter': 'Mihailo St. Popović',
    'title': 'On the Usefulness of OpenAtlas in Historical Geography',
    'conference': '',
    'location': [_('Belgrade')],
    'date': get_table_dates_formatted(2023, 9, 19),
    'external_link': '',
    'download': '',
    'category': ['holdura']
}, {
    'presenter': 'Johannes Tripps',
    'title': 'The Metamorphosing crown of Saint Stefan Decanski',
    'conference': '',
    'location': [_('Belgrade')],
    'date': get_table_dates_formatted(2023, 9, 7),
    'external_link': 'https://www.youtube-nocookie.com/'
                     'embed/HF7fLgHFnaI?si=AIghTnDMknsnvlvm',
    'download': '',
    'category': ['holdura']
}, {
    'presenter': 'Branka Vranešević',
    'title':
        'Initials with Teratological Motifs in the Belgrade Prophetologion: '
        'Witnesses of Entanglement between East and West',
    'conference': 'International Medieval Congress',
    'location': [_('Leeds')],
    'date': get_table_dates_formatted(2023, 7, 6),
    'external_link': '',
    'download': '',
    'category': ['holdura']
}, {
    'presenter': 'Johannes Tripps',
    'title':
        'Objects of Private Devotion as Witnesses to Entanglement between '
        'Venice and the Árpád and Nemanjić Dynasties',
    'conference': 'International Medieval Congress',
    'location': [_('Leeds')],
    'date': get_table_dates_formatted(2023, 7, 6),
    'external_link': '',
    'download': '',
    'category': ['holdura']
}, {
    'presenter': 'Bernhard Koschiček-Krombholz',
    'title':
        'OpenAtlas: Handling Entangled Data in a Linked Data World',
    'conference': 'International Medieval Congress',
    'location': [_('Leeds')],
    'date': get_table_dates_formatted(2023, 7, 6),
    'external_link': '',
    'download': '',
    'category': ['holdura']
}, {
    'presenter': 'Mihailo St. Popović',
    'title':
        'A Mother and Two Sons: the Serbian Rulers Helen, Dragutin, and '
        'Milutin and Their Entangled Realms in Medieval Serbia',
    'conference': 'International Medieval Congress',
    'location': [_('Leeds')],
    'date': get_table_dates_formatted(2023, 7, 6),
    'external_link': '',
    'download': '',
    'category': ['holdura']
}, {
    'presenter': 'Dorota Vargová',
    'title':
        'Stefan Uroš I and Helen of Anjou: The Royal Couple\'s Influence on '
        'the Confessional Structure of the Principality of Zeta in the Late '
        '13th and Early 14th Century ',
    'conference': 'International Medieval Congress',
    'location': [_('Leeds')],
    'date': get_table_dates_formatted(2023, 7, 6),
    'external_link': '',
    'download': '',
    'category': ['holdura']
}, {
    'presenter': 'Mihailo St. Popović',
    'title':
        'Пројекат Tabula Imperii Byzantini: о будућности (?) проучавања '
        'историјске географије Византије ',
    'conference': 'Serbian Academy of Sciences and Arts – SANU',
    'location': [_('Belgrade')],
    'date': get_table_dates_formatted(2022, 2, 22),
    'external_link': '',
    'download': '',
    'category': ['holdura']
}, {
    'presenter': 'Mihailo St. Popović',
    'title':
        'Die historische Geographie von Byzanz neu gedacht – Über den '
        'Wert der digitalen Kartographie und Geokommunikation in der '
        'Vermittlung historischer Inhalte am Beispiel des Projektes '
        '„Jenseits von Ost und West“',
    'conference':
        'Deutsche Gesellschaft für Kartographie e.V., '
        'Sektion Halle – Leipzig',
    'location': [_('Leipzig')],
    'date': get_table_dates_formatted(2022, 11, 10),
    'external_link': '',
    'download': '',
    'category': ['holdura']
}, {
    'presenter': 'Mihailo St. Popović',
    'title':
        'Doing Historical Geography in A Digital Age: The Case of The '
        'Tabula Imperii Byzantini Balkans and Its Public Outreach',
    'conference': '2022 Byzantine Studies Conference',
    'location': [_('Los Angeles')],
    'date': get_table_dates_formatted(2022, 11, 6),
    'external_link': 'https://bsana.net/annual-conference/',
    'download': '',
    'category': ['holdura']
}, {
    'presenter': 'Mihailo St. Popović',
    'title':
        'Historical Geography, Digital Humanities and Database Systems: '
        'an Approach to reconstruct “Sacred Landscapes” – the Case of '
        'Medieval Duklja and Raška (today’s Montenegro and Serbia)',
    'conference':
        'Global Eurasia, Workshop II: Handlungsspielräume, Netzwerke und '
        'transregionale Kontexte',
    'location': [_('Vienna')],
    'date': get_table_dates_formatted(2022, 5, 12),
    'external_link': '',
    'download': '',
    'category': ['holdura']
}, {
    'presenter': 'Mihailo St. Popović',
    'title':
        'On the Use and Usefulness of Digital Humanities in the '
        'Historical Geography of Byzantium',
    'conference':
        'Seminar Series: The Balkans Between Empires, Aristotle '
        'University of Thessaloniki, Ibn Haldun University Istanbul',
    'location': [_('Thessaloniki')],
    'date': get_table_dates_formatted(2022, 4, 1),
    'external_link': '',
    'download': '',
    'category': ['holdura']
}, {
    'presenter': 'Markus Breier',
    'title':
        'Beyond East and West – '
        'Geocommunicating Historical Sacred Landscapes',
    'conference': 'International Medieval Congress, University of Leeds',
    'location': [_('Leeds')],
    'date': get_table_dates_formatted(2021, 7, 7),
    'external_link': '',
    'download': '',
    'category': ['holdura']
}, {
    'presenter':
        'Markus Breier, Karel Kriz, Lukas Neugebauer, Alexander Pucher',
    'title':
        'Beyond East and West – '
        'Geocommunicating Historical Sacred Landscapes',
    'conference': '30th International Cartographic Conference 2021',
    'location': [_('Florenz')],
    'date': get_table_dates_formatted(2021, 12, 18),
    'external_link': '',
    'download': '',
    'category': ['holdura']
}, {
    'presenter': 'Dorota Vargová',
    'title':
        'An Ecclesiastical History of Medieval Duklja:'
        ' A Landscape Defined by Rite',
    'conference': 'International Medieval Congress',
    'location': [_('Leeds')],
    'date': get_table_dates_formatted(2022, 7, 6),
    'external_link': '',
    'download': '',
    'category': ['holdura']
}, {
    'presenter': 'Branka Vranešević',
    'title':
        'Towards Imperial Dignity: A Contribution to the Study of the '
        'Imperial Crown of King Stefan Uroš III Dečanski in the '
        'Cetinje Monastery',
    'conference': 'International Medieval Congress',
    'location': [_('Leeds')],
    'date': get_table_dates_formatted(2022, 7, 6),
    'external_link': '',
    'download': '',
    'category': ['holdura']
}, {
    'presenter': 'Moisés Hernández Cordero',
    'title':
        'Mapping Cultural Heritage beyond the Eye: The Case of the Crown '
        'of the Serbian King Stefan Dečanski',
    'conference': 'International Medieval Congress',
    'location': [_('Leeds')],
    'date': get_table_dates_formatted(2022, 7, 6),
    'external_link': '',
    'download': '',
    'category': ['holdura', 'montenegro']
}, {
    'presenter': 'Mihailo Popović',
    'title':
        'Beyond East and West: Sacred Landscapes in the Territory of '
        'Today\'s Montenegro, 11th-14th Centuries',
    'conference': 'International Medieval Congress',
    'location': [_('Leeds')],
    'date': get_table_dates_formatted(2022, 7, 6),
    'external_link': '',
    'download': '',
    'category': ['holdura']
}, {
    'presenter': 'Markus Breier',
    'title':
        'Modern Cartographic Representations of Medieval Borders '
        'and Border Zones',
    'conference': 'International Medieval Congress',
    'location': [_('Leeds')],
    'date': get_table_dates_formatted(2022, 7, 6),
    'external_link': '',
    'download': '',
    'category': ['holdura']
}, {
    'presenter': 'Lukas Neugebauer',
    'title':
        'Experiencing Historical Landscapes Using Visual Storytelling',
    'conference': 'International Medieval Congress',
    'location': [_('Leeds')],
    'date': get_table_dates_formatted(2022, 7, 6),
    'external_link': '',
    'download': '',
    'category': ['holdura']
}, {
    'presenter': 'Markus Breier',
    'title':
        'Beyond East and West - A Framework for Researching and '
        'Communicating Historical Landscapes',
    'conference': 'EuroCarto 2022',
    'location': [_('Vienna')],
    'date': get_table_dates_formatted(2022, 9, 19),
    'external_link': '',
    'download': 'eurocarto_2022.pdf',
    'category': ['holdura']
}, {
    'presenter': 'Markus Breier',
    'title':
        'The Sacred Landscape of Medieval Montenegro: '
        'Map-Based Communication',
    'conference':
        '5. Geographie-Werkstatt des Österreichischem Geographieverbands',
    'location': [_('Vienna')],
    'date': get_table_dates_formatted(2022, 9, 20),
    'external_link': '',
    'download': '2022-09-20_Geographiewerkstatt_Poster.jpg',
    'category': ['holdura']
}]
