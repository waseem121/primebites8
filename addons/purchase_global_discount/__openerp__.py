# -*- coding: utf-8 -*-
{
    'name': "Purchase Global Discount",

    'summary': """
    """,

    'description': """
Purchase Global Discount
========================
Option to set fix and percentage discount.

Percentage Discount
-------------------
This is set on every purchase order line.

Fixed Discount
--------------
A new line is added with description as Fix Discount and discount amount as -ve unit price.
    """,

    'author': "Aasim Ahmed Ansari",
    'website': "http://aasimania.wordpress.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase','product'],

    # always loaded
    'data': [
        'security/purchase_security.xml',
        'wizard/purchase_global_discount_wizard_view.xml',
        'purchase_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}