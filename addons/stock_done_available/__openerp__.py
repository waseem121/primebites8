# -*- coding: utf-8 -*-
{
    'name': "Stock Done only if Available",

    'summary': """
    """,

    'description': """
        Features:
        * Blocks stock moves from Ready to Transfer state if not enough stock.
        * Special group assigned to Force Availability button. 
        * When Check Availability button is clicked, stock move is updated with latest cost price.
    """,

    'author': "Aasim Ahmed Ansari",
    'website': "http://aasimania.wordpress.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
         'security/stock_security.xml',
        'stock_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
#        'demo.xml',
    ],
}