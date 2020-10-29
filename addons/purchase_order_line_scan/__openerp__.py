# -*- coding: utf-8 -*-
{
    'name': "purchase_order_line_scan",

    'summary': """
        Product scanning in Purchase Order""",

    'description': """
Product scanning in Purchase Order
==================================

Features
--------
    * Allows scanning of product from purchase form view
    * System picks up default UoM configured in product master
    """,

    'author': "Aasim Ahmed Ansari",
    'website': "http://aasimania.wordpress.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/purchase_order_line_scan_view.xml',
        'purchase_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}