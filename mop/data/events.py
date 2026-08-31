from flask_babel import lazy_gettext as _

from mop.data.team import team
from mop.util import get_dates_formatted

types = {
    'presentation': {
        'name': _('presentation'),
        'bs_icon': 'bi-chat-text-fill'},
    'online_presentation': {
        'name': _('presentation'),
        'bs_icon': 'bi-chat-right-text-fill'},
    'award': {
        'name': _('award'),
        'bs_icon': 'bi-award'},
    'science_fair': {
        'name': _('science_fair'),
        'bs_icon': 'bi-mortarboard-fill'},
    'book_release': {
        'name': _('book_release'),
        'bs_icon': 'bi-book'},
    'blog_post': {
        'name': _('blogpost'),
        'bs_icon': 'bi-blockquote-right'},
    'press_release': {
        'name': _('press_release'),
        'bs_icon': 'bi-newspaper'}}
event_list = [{
    'id': 'didip_230726',
    'type': types['presentation'],
    'date': f"{get_dates_formatted(2026, 7, 23)}",
    'who': '',
    'icon': 'didip_230726.jpg',
    'title': _('Presentation at the DiDip Conference'),
    'description': _('didip_230726'),
    'attachment': [{
        'path': '',
        'type': ''
    }]
}, {
    'id': 'imc_leeds_26',
    'type': types['presentation'],
    'date': f"{get_dates_formatted(2026, 7, 7)}",
    'who': '',
    'icon': 'imc_leed_26.jpg',
    'title': _('Session at the IMC in Leeds'),
    'description': _('imc_leeds_26'),
    'attachment': [{
        'path': '',
        'type': ''
    }]
}, {
    'id': 'lange_nacht_der_forschung_240426',
    'type': types['presentation'],
    'date': f"{get_dates_formatted(2026, 4, 24)}",
    'who': '',
    'icon': 'lange_nacht_der_forschung_240426.jpg',
    'title': _('Lange Nacht der Forschung 2026'),
    'description': _('lange_nacht_der_forschung_240426'),
    'attachment': [{
        'path': '',
        'type': ''
    }]
}, {
    'id': 'brno_summer_school_260625',
    'type': types['presentation'],
    'date': f"{get_dates_formatted(2025, 6, 26)}",
    'who': '',
    'icon': 'brno_summer_school_260625.jpg',
    'title': _('Summer School in Brno'),
    'description': _('brno_summer_school_260625'),
    'attachment': [{
        'path': '',
        'type': ''}]
}, {
    'id': 'heidelberg_200625',
    'type': types['presentation'],
    'date': f"{get_dates_formatted(2025, 6, 20)}",
    'who': '',
    'icon': 'heidelberg_200625.jpg',
    'title': _('Discourse on DH and AI'),
    'description': _('heidelberg_200625'),
    'attachment': [{
        'path': '',
        'type': ''}]
}, {
    'id': 'presse_03052025',
    'type': types['press_release'],
    'date': f"{get_dates_formatted(2025, 5, 3)}",
    'who': '',
    'icon': 'presse_03052025.jpg',
    'title': _('Report in the Newspaper Die Presse'),
    'description': _('presse_03052025'),
    'attachment': [{
        'path': '',
        'type': ''}]
}, {
    'id': 'wittgenstein_13022025',
    'type': types['presentation'],
    'date': f"{get_dates_formatted(2025, 2, 13)}",
    'who': '',
    'icon': 'wittgenstein_13022025.jpg',
    'title': _('Lecture at the Haus Wittgenstein'),
    'description': _('wittgenstein_13022025'),
    'attachment': [{
        'path': '',
        'type': ''}]
}, {
    'id': 'workshop_oxford_300524',
    'type': types['science_fair'],
    'date': f"{get_dates_formatted(2024, 5, 30)}",
    'who': '',
    'icon': 'workshop_oxford_300524.jpg',
    'title': _('Workshop in Oxford'),
    'description': _('workshop_oxford_300524'),
    'attachment': [{
        'path': '',
        'type': ''
    }]
}, {
    'id': 'lange_nacht_der_forschung_240524',
    'type': types['presentation'],
    'date': f"{get_dates_formatted(2024, 5, 24)}",
    'who': '',
    'icon': 'lange_nacht_der_forschung_240524.jpg',
    'title': _('The Long Night of Research in Vienna'),
    'description': _('lange_nacht_der_forschung_240524'),
    'attachment': [{
        'path': '',
        'type': ''
    }]
}, {
    'id': 'koder_festschrift_230424',
    'type': types['book_release'],
    'date': f"{get_dates_formatted(2024, 4, 23)}",
    'who': '',
    'icon': 'koder_festschrift_230424.jpg',
    'title': _('Presentation of an Edited Volume in Honor of Johannes Koder'),
    'description': _('koder_festschrift_230424'),
    'attachment': [{
        'path': '',
        'type': ''
    }]}, {
        'id': 'belgrade_190923',
        'type': types['presentation'],
        'date': f"{get_dates_formatted(2023, 9, 19)}",
        'who': '',
        'icon': 'belgrade_190923.png',
        'title': _('Two Presentations on the Usefulness of OpenAtlas'),
        'description': _('belgrade_190923'),
        'attachment': [{
            'path': '',
            'type': ''}]
    }, {
        'id': 'athos_oxford_290923',
        'type': types['presentation'],
        'date': f"{get_dates_formatted(2023, 9, 29)}",
        'who': [team['mpopovic']],
        'icon': 'athos_oxford_290923.png',
        'title': _('Workshop on Medieval Athos in Oxford'),
        'description': _('athos_oxford_290923'),
        'attachment': [{
            'path': '',
            'type': ''}]
    }, {
        'id': 'tripps_070923',
        'type': types['presentation'],
        'date': f"{get_dates_formatted(2023, 9, 7)}",
        'who': '',
        'icon': 'tripps_070923.jpg',
        'title': _('Paper on the Crown of the Saint King Stefan Dečanski'),
        'description': _('tripps_070923'),
        'attachment': [{
            'path': '',
            'type': ''}]
    }, {
        'id': 'imc_leeds_23',
        'type': types['presentation'],
        'date': f"{get_dates_formatted(2023, 7, 6)}",
        'who': '',
        'icon': 'imc_leeds_23.jpg',
        'title': _('TIB Balkans at the IMC Leeds 2023'),
        'description': _('imc_leeds_23'),
        'attachment': [{
            'path': '',
            'type': ''}]
    }, {
        'id': 'mecern_2023',
        'type': types['presentation'],
        'date': f"{get_dates_formatted(2023, 4, 27)}",
        'who': [team['mpopovic']],
        'icon': 'mecern_2023.jpg',
        'title': _('presentation on MECERN conference'),
        'description': _('mecern_2023'),
        'attachment': [{
            'path': '',
            'type': ''
        }]
    }, {
        'id': 'serbian_academy_220223',
        'type': types['presentation'],
        'date': f"{get_dates_formatted(2023, 2, 22)}",
        'who': [team['mpopovic']
               ],
        'icon': 'serbian_academy_220223.jpg',
        'title': _('presentation at the Serbian Academy of Sciences and Arts'),
        'description': _('serbian_academy_220223'),
        'attachment': [{
            'path': '',
            'type': ''}]}, {
        'id': 'les_ciutats_mediterranies_151222',
        'type': types['presentation'],
        'date': f"{get_dates_formatted(2022, 12, 15)}",
        'who': [team['mpopovic']],
        'icon': 'lead_seals_2022.jpg',
        'title': _('Presentation in Barcelona'),
        'description': _(
            'Andreas Külzer and Mihailo Popović gave a joint paper entitled '
            '"Reality and Mirage in the Eastern Mediterranean. The Long Term '
            'Project Tabula Imperii Byzantini and its Reconstruction Work of '
            'Late Antique and Medieval Settlements" at the conference '
            '“Les ciutats mediterrànies. Realitat i miratge” in Barcelona '
            'on 15 December 2022.'),
        'attachment': [{
            'path': '/repository/Prog_Ciutats_Mediterranies_2022.pdf',
            'type': 'pdf'}]}, {
        'id': 'tib11_promotion_141122',
        'type': types['award'],
        'date': f"{get_dates_formatted(2022, 11, 14)}",
        'who': [team['mpopovic']],
        'icon': 'tib11_promotion.jpg',
        'title': _('Promotion Event for TIB 11'),
        'description': _(
            'On Monday, 14 November 2022, the TIB volume "Macedonia, '
            'Southern Part" (TIB 11) was presented to the public at the '
            'Austrian Academy of Sciences in Vienna.'),
        'attachment': [{
            'path': '/repository/ABF_Buchpraesentation_TIB_11.pdf',
            'type': 'pdf'}]}, {
        'id': 'histgeo_leipzig_101122',
        'type': types['presentation'],
        'date': f"{get_dates_formatted(2022, 11, 10)}",
        'who': [team['mpopovic']],
        'icon': 'histgeo_leipzig_22.jpg',
        'title': _('Presentation in Leipzig'),
        'description': _(
            'Mihailo Popović presented a paper in Leipzig on the historical '
            'geography of Byzantium and the ongoing research of the TIB on '
            '10 November 2022.'),
        'attachment': [{
            'path': '/repository/Popovic_11_22.pdf',
            'type': 'pdf'}]}, {
        'id': 'aieb_roundtable_220822',
        'type': types['presentation'],
        'date': '22.08.2022-27.08.2022',
        'who': [team['mpopovic']],
        'icon': 'aieb_roundtable_icon.jpg',
        'title': _(
            '24th International Congress of Byzantine Studies in '
            'Venice and Padua'),
        'description': _(
            'The AIEB Commission for the Historical Geography and Spatial '
            'Analysis of Byzantium organised a Round Table entitled '
            '"Historical Geography of Byzantium in a Digital Age: Chances '
            'and Risks" at the 24th International Congress of Byzantine '
            'Studies in Venice and Padua (22–27 August 2022).'),
        'attachment': [{
            'path': '',
            'type': ''}]}, {
        'id': 'hypotheses_post_150822',
        'type': types['blog_post'],
        'date': f"{get_dates_formatted(2022, 8, 15)}",
        'who': [team['bkoschicek'], team['mpopovic']],
        'icon': 'blog_post.png',
        'title': _('Blogpost on "OpenAtlas und historische Geographie"'),
        'description': _(
            'The paper "OpenAtlas und historische Geographie: Die Tabula '
            'Imperii Byzantini (Balkan) im digitalen Zeitalter" by Bernhard '
            'Koschiček-Krombholz and Mihailo St. Popović was discussed and '
            'commented in a blogpost on dhc.hypotheses.org.'),
        'attachment': [{
            'path': '',
            'type': ''}]}, {
        'id': 'tib11_release_260722',
        'type': types['book_release'],
        'date': f"{get_dates_formatted(2022, 7, 26)}",
        'who': [team['mpopovic']],
        'icon': 'tib11_release.jpg',
        'title': _('TIB Volume 11, Macedonia, Southern Part Published'),
        'description': _(
            'Publication of TIB Volume 11 ("Macedonia, Southern Part") '
            'written by Peter Soustal with Andreas Pülz and Mihailo St. '
            'Popović as co-authors.'),
        'attachment': [{
            'path': '/repository/TIB_11_macedonia_southern_part.pdf',
            'type': 'pdf'}]}, {
        'id': 'imc_leeds_060722',
        'type': types['presentation'],
        'date': f"{get_dates_formatted(2022, 7, 6)}",
        'who': [team['mpopovic']],
        'icon': 'leeds_22_icon.jpg',
        'title': _('Presentation at the IMC in Leeds 2022'),
        'description': _(
            'During the International Medieval Congress (IMC) in Leeds '
            'from 4 to 7 July 2022, the team of the TIB Balkans presented '
            'its research in sessions on historical geography and spatial '
            'analysis.'),
        'attachment': [{
            'path': '',
            'type': ''}]}, {
        'id': 'seminar_koeln_230622',
        'type': types['presentation'],
        'date': f"{get_dates_formatted(2022, 6, 23)}",
        'who': [team['bkoschicek'], team['mpopovic']],
        'icon': 'koeln_icon.jpg',
        'title': _('Presentation at the University of Cologne'),
        'description': _(
            'Bernhard Koschiček-Krombholz and Mihailo St. Popović presented '
            'a paper on "OpenAtlas und historische Geographie: Die Tabula '
            'Imperii Byzantini (Balkan) im digitalen Zeitalter" at a Digital '
            'Humanities colloquium of the University of Cologne.'),
        'attachment': [{
            'path': '',
            'type': ''}]}, {
        'id': 'lange_nacht_200522',
        'type': types['science_fair'],
        'date': f"{get_dates_formatted(2022, 5, 20)}",
        'who': [team['mpopovic']],
        'icon': 'lange_nacht_icon.jpg',
        'title': _('TIB at the Lange Nacht der Forschung 2022'),
        'description': _(
            'The Long-Term Project Tabula Imperii Byzantini communicated '
            'its newest research output to the public at the Austrian '
            'nationwide Lange Nacht der Forschung 2022 with discovery '
            'activities and presentations.'),
        'attachment': [{
            'path': '',
            'type': ''}]}, {
        'id': 'global_eurasia_120522',
        'type': types['presentation'],
        'date': f"{get_dates_formatted(2022, 5, 12)}",
        'who': [team['mpopovic']],
        'icon': 'global_eurasia_icon.jpg',
        'title': _(
            'Presentation at "Global Eurasia – Comparison and Connectivity '
            'II"'),
        'description': _(
            'Mihailo Popović presented a paper on the TIB at the conference '
            '“Global Eurasia – Comparison and Connectivity II: Agency, '
            'Networks and Transregional Contexts” at the IMAFO (ÖAW).'),
        'attachment': [{
            'path': '',
            'type': ''}]}, {
        'id': 'lead_seals_190422',
        'type': types['presentation'],
        'date': f"{get_dates_formatted(2022, 4, 19)}",
        'who': [team['mpopovic']],
        'icon': 'lead_seals_2022.jpg',
        'title': _('Congress on Byzantine Thrace: Lead Seals'),
        'description': _(
            'The TIB and its researchers took part substantially in the '
            'conference “Lead Seals in Byzantine Thrace” at the IMAFO of '
            'the ÖAW on 19 April 2022.'),
        'attachment': [{
            'path': '/repository/Lead-Seals-in-Byzantine-Thrace.pdf',
            'type': 'pdf'}]}, {
        'id': 'seminar_series_010422',
        'type': types['presentation'],
        'date': f"{get_dates_formatted(2022, 4, 1)}",
        'who': [team['mpopovic']],
        'icon': 'seminar_series_icon.jpg',
        'title': _('Lecture on Digital Humanities in Historical Geography'),
        'description': _(
            'Mihailo Popović gave an online lecture entitled “On the Use '
            'and Usefulness of Digital Humanities in the Historical '
            'Geography of Byzantium” on 1 April 2022 as part of the '
            'seminar series “The Balkans Between Empires”.'),
        'attachment': [{
            'path': '/repository/Seminar-Poster-Popovic.pdf',
            'type': 'pdf'}]}]
