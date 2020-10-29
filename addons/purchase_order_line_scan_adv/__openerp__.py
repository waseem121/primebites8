# -*- coding: utf-8 -*-
{
    'name': "Purchase Order Line Scan Advanced",

    'summary': """
    """,

    'description': """
        Purchase Order Line Scan Advanced
    """,

    'author': "Aasim Ahmed Ansari",
    'website': "http://aasimania.wordpress.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Purchase Management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizard/purchase_order_line_scan_view.xml',
        'view/purchase.xml',
        'purchase_view.xml',
    ],
    'qweb' : [
        'static/src/xml/purchase_order_line_scan.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}