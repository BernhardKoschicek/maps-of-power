from flask_babel import lazy_gettext as _

institutes = {
    'sasa': {
        'name': _('Institute for Byzantine Studies '
                  'of the Serbian Academy of Sciences and Arts'),
        'url': 'https://www.sanu.ac.rs/en/sasa-institutes/'
               'institute-for-byzantine-studies/',
        'logo': 'sasa.png',
        'member': '',
        'address': ''},
    'sfrs': {
        'name': _('Science Fund of the Republic of Serbia'),
        'url': 'https://fondzanauku.gov.rs/?lang=en',
        'logo': 'sfrs.png',
        'member': '',
        'address': ''},
    'zf': {
        'name': _('Zukunftsfonds'),
        'url': 'http://www.zukunftsfonds-austria.at/',
        'logo': 'zf_logo.jpg',
        'member': '',
        'address': ''},
    'dfg': {
        'name': _('Deutsche Forschungsgemeinschaft'),
        'url': 'https://www.dfg.de/',
        'logo': 'dfg_inv.png',
        'member': '',
        'address': ''},
    'mt': {
        'name': _('Metropolis von Austria'),
        'url': 'http://www.metropolisvonaustria.at/',
        'logo': 'metropolis.png',
        'member': _('S. Em. Metropolit Arsenios von Austria'),
        'address': _('Fleischmarkt 13<br>1010 Wien<br>Österreich')},
    'oeaw': {
        'name': _('Austrian Academy of Sciences'),
        'url': 'https://www.oeaw.ac.at/',
        'logo': 'oeaw.png',
        'member': '',
        'address': ''},
    'oeai': {
        'name': _('Austrian Archaeological Institute'),
        'url': 'https://www.oeaw.ac.at/en/oeai/',
        'logo': 'oeai.jpg',
        'member': '',
        'address': ''},
    'imafo': {
        'name': _('Institute for Medieval Research'),
        'url': 'https://www.oeaw.ac.at/imafo/',
        'logo': 'imafo.png',
        'member': '',
        'address': ''},
    'abf': {
        'name': _('Abteilung Byzanzforschung (ABF)'),
        'url': 'https://www.oeaw.ac.at/byzanz',
        'logo': 'imafo.png',
        'member': _('Österreichische Akademie der Wissenschaften (ÖAW) '
                     '<br> Institut für Mittelalterforschung (IMAFO)'),
        'address': ''},
    'acdh-ch': {
        'name': _('Austrian Centre for Digital Humanities and Cultural Heritage'),
        'url': 'https://www.oeaw.ac.at/acdh/',
        'logo': 'acdh.png',
        'member': '',
        'address': ''},
    'univie': {
        'name': _('University of Vienna'),
        'url': 'https://www.univie.ac.at/',
        'logo': 'uni_vienna.png',
        'member': '',
        'address': ''},
    'fwf': {
        'name': _('Austrian Science Fund'),
        'url': 'https://www.fwf.ac.at/',
        'logo': 'fwf.svg',
        'member': '',
        'address': ''},
    'oenb': {
        'name': _('Jubiläumsfonds der Oesterreichischen Nationalbank'),
        'url': 'https://www.oenb.at/Ueber-Uns/'
               'Forschungsfoerderung/Jubilaeumsfonds.html',
        'logo': 'oenb.png',
        'member': '',
        'address': ''},
    'oead': {
        'name': _('Austrian Agency for International'
                  ' Cooperation in Education and Research'),
        'url': 'https://oead.at/de/',
        'logo': 'oead.svg',
        'member': '',
        'address': ''},
    'ma7': {
        'name': _('Wien Kultur (MA 7)'),
        'url': 'https://www.wien.gv.at/kultur/abteilung/',
        'logo': 'wien-kultur.png',
        'member': '',
        'address': ''},
    'ait': {
        'name': _('Austrian Institute of Technology'),
        'url': 'https://www.ait.ac.at/',
        'logo': 'ait.jpg',
        'member': '',
        'address': ''},
    'bcm': {
        'name': _('Belgrade City Museum'),
        'url': 'http://www.mgb.org.rs/en/',
        'logo': 'bcm.png',
        'member': '',
        'address': ''},
    'bg_uni': {
        'name': _('University of Belgrade'),
        'url': 'https://www.bg.ac.rs/',
        'logo': 'belgrad_university.png',
        'member': '',
        'address': ''},
    'nls': {
        'name': _('National Library of Serbia'),
        'url': 'https://www.nb.rs',
        'logo': 'nls.jpg',
        'member': '',
        'address': ''},
    'bms': {
        'name': _('Biblioteka Matice Srpske'),
        'url': 'http://www.bms.ns.ac.rs/bms101.htm',
        'logo': 'biblioteka_matice_srpske.png',
        'member': '',
        'address': ''},
    'tib': {
        'name': _('Tabula Imperii Byzantini'),
        'url': 'https://tib.oeaw.ac.at',
        'logo': 'tib.png',
        'member': '',
        'address': ''},
    'uai': {
        'name': _('Union Académique Internationale'),
        'url': 'http://www.uai-iua.org/en',
        'logo': 'uai.jpg',
        'member': '',
        'address': ''},
    'noe': {
        'name': _('Land Niederösterreich, Abteilung Wissenschaft und Forschung'),
        'url': 'https://sciencecenter.noe.gv.at/massnahme/'
               '4da6e8c1-306b-4381-b20a-4128644b95b3',
        'logo': 'noe.jpg',
        'member': '',
        'address': ''},
    'iti': {
        'name': _('Katholische Hochschule ITI'),
        'url': 'https://iti.ac.at/',
        'logo': 'iti.png',
        'member': '',
        'address': ''},
    'om': {
        'name': _('Orient & Méditerranée'),
        'url': 'https://www.orient-mediterranee.com/',
        'logo': 'logo-om_2.svg',
        'member': '',
        'address': ''},
    'ukim': {
        'name': _('Ss. Cyril and Methodius University'),
        'url': 'https://www.ukim.edu.mk/',
        'logo': 'ukim_i_fzf.png',
        'member': '',
        'address': ''}
}
