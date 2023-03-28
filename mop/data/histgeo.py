from flask_babel import lazy_gettext as _

newsletters = {
    '2019': [{
        'title': _('march'),
        'url': 'https://t210d45f9.emailsys2a.net/mailing/180/1931555/0/4c8ef08a44/index.html'
    }, {
        'title': _('june'),
        'url': 'https://t210d45f9.emailsys2a.net/mailing/180/2098849/0/f89bc47dd2/index.html'
    }, {
        'title': _('september'),
        'url': 'https://t210d45f9.emailsys2a.net/mailing/180/2304029/0/ae2843a1db/index.html'
    }, {
        'title': _('december'),
        'url': 'https://t210d45f9.emailsys2a.net/mailing/180/2473597/0/aa3077aebc/index.html'
    }],
    '2020': [{
        'title': _('march'),
        'url': 'https://t210d45f9.emailsys2a.net/mailing/180/2695141/1800344/67/a3037fe6ef/index.html'
    }, {
        'title': _('june'),
        'url': 'https://t210d45f9.emailsys2a.net/mailing/180/3027457/0/2b15372ebf/index.html'
    }, {
        'title': _('september'),
        'url': 'https://t210d45f9.emailsys2a.net/mailing/180/3290677/0/e213d9d6ef/index.html'
    }, {
        'title': _('december'),
        'url': 'https://t210d45f9.emailsys2a.net/mailing/180/3551107/0/6bb9bf3335/index.html'
    }],
    '2021': [{
        'title': _('march'),
        'url': 'https://t210d45f9.emailsys2a.net/mailing/180/3919231/0/d9dd25f276/index.html'
    }, {
        'title': _('june'),
        'url': 'https://t210d45f9.emailsys2a.net/mailing/180/4245827/1796772/b715f05a17/index.html'
    }, {
        'title': _('september'),
        'url': 'https://t210d45f9.emailsys2a.net/mailing/180/4549023/0/2c8778ca96/index.html'
    }, {
        'title': _('december'),
        'url': 'https://t210d45f9.emailsys2b.net/mailing/180/4858583/9401703/1373/38501319f6/index.html'
    }],
    '2022': [{
        'title': _('march') + '-' + _('june'),
        'url': 'https://t210d45f9.emailsys2a.net/mailing/180/5374373/0/3d244bbdd7/index.html'
    }, {
        'title': _('september') + '-' + _('december'),
        'url': 'https://t210d45f9.emailsys2a.net/mailing/180/6008245/0/e74da87270/index.html'
    }],
}


volumes = {
    1: {
        'title': 'Space, Landscapes and Settlements in Byzantium. Studies in '
                 'Historical Geography of the Eastern Mediterranean Presented '
                 'to Johannes Koder',
        'author': 'Andreas Külzer, Mihailo St. Popović ' + _('eds.'),
        'abstract': [_('histgeo_vol1_1'), _('histgeo_vol1_2'),
                     _('histgeo_vol1_3')],
        'order': 'https://akademskaknjiga.com/katalog/space-landscapes-and-settlements-in-byzantium/',
        'ISBN': '978-86-6263-191-6',
        'pages': '526',
        'citation': 'Andreas Külzer, Mihailo St. Popović (eds.), Space, '
                    'Landscapes and Settlements in Byzantium. Studies in '
                    'Historical Geography of the Eastern Mediterranean '
                    'Presented to Johannes Koder (Studies in Historical '
                    'Geography and Cultural Heritage 1). Vienna–Novi Sad '
                    '(Akademska knjiga) 2017.',
    },
    2: {
        'title': 'Herbert Hunger und die Wiener Schule der Byzantinistik',
        'author': 'Andreas Külzer ' + _('ed.'),
        'abstract': [_('histgeo_vol2_1')],
        'order': 'https://akademskaknjiga.com/katalog/herbert-hunger-und-die-wiener-schule-der-byzantinistik/',
        'ISBN': '978-86-6263-243-2',
        'pages': '352',
        'citation': 'Andreas Külzer (ed.), Herbert Hunger und die Wiener '
                    'Schule der Byzantinistik (Studies in Historical Geography '
                    'and Cultural Heritage 2). Vienna–Novi Sad (Akademska '
                    'knjiga) 2019.',
    },
    3: {
        'title': 'Raum und Geschichte: der historische Atlas \'Tabula Imperii '
                 'Byzantini (TIB)\' an der Österreichischen Akademie der '
                 'Wissenschaften ',
        'author': 'Andreas Külzer, Veronika Polloczek, Mihailo St. Popović '
                  + _('eds.'),
        'abstract': [_('histgeo_vol3_1')],
        'order': 'https://akademskaknjiga.com/katalog/raum-und-geschichte-der-historische-atlas-tabula-imperii-byzantini-an-der-osterreichischen-akademie-der-wissenschaften-2/ ',
        'ISBN': '978-86-6263-305-7',
        'pages': '240',
        'citation': 'Andreas Külzer, Veronika Polloczek, Mihailo St. Popović '
                    '(eds.), Raum und Geschichte: der historische Atlas '
                    '\'Tabula Imperii Byzantini (TIB)\' an der '
                    'Österreichischen Akademie der Wissenschaften (Studies in '
                    'Historical Geography and Cultural Heritage 3). '
                    'Vienna–Novi Sad (Akademska knjiga) 2020.',
    },
    4: {
        'title': 'Ermitages et monastères rupestres de la Laconie byzantine '
                 '(XIe-XVe siècle) : Archéologie, topographie et paysages ',
        'author': 'Ludovic Bender',
        'abstract': [_('histgeo_vol4_1')],
        'order': 'https://akademskaknjiga.com/katalog/ermitages-et-monasteres-rupestres-byzantins-de-laconie-peloponnese-archeologie-et-paysages/',
        'ISBN': '978-86-6263-305-7',
        'pages': '464',
        'citation': 'Ludovic Bender, Ermitages et monastères rupestres de la '
                    'Laconie byzantine (XIe-XVe siècle) : Archéologie, '
                    'topographie et paysages (Studies in Historical Geography '
                    'and Cultural Heritage 4). Vienna–Novi Sad (Akademska '
                    'knjiga) 2022.',
    },
    5: {
        'title': 'Contribution to the Prosopography of the Borderzone. '
                 'Migration and Elite Change in Pre-Ottoman Macedonia',
        'author': 'Vratislav Zervan',
        'abstract': [],
        'order': '',
        'ISBN': '',
        'pages': '',
        'citation': '',
    },
}

_('author')
_('pages')
_('ISBN')
_('citation')
_('order')
_('abstract')
