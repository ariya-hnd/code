{
    'name': 'XXI Pos Note Customer',
    'summary': """XXI Pos Note Customer""",
    'version': '10.0.1.0',
    'description': """Manually add customer name in pos receipt""",
    'author': 'HashMicro/ MPTechnolabs(Chankya) / MP Technolabs- Purvi',
    'website': 'http://www.hashmicro.com',
    'category': 'Point Of Sale',
    'depends': ['xxi_modifier_printout'],
    'data': ['views/template.xml'],
    'qweb':  ['static/src/xml/pos_customer_note.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
