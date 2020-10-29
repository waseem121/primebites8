# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Acespritech Solutions Pvt Ltd
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Acespritech Barcode Label',
    'version': '1.1',
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'category': 'Product',
    'description': """
        Product custom label design. User can change the sequence of fields to display in label.
    """,
    'website': 'https://www.acespritech.com',
    'summary': 'Product custom label design. User can change the sequence of fields to display in label.',
    'depends': ['base', 'sale', 'product'],
    'data': [
         'security/ir.model.access.csv',
         'wizard/aces_small_barcode_label_view.xml',
         'aces_barcode_label_report.xml',
         'views/product_barcode_report_template.xml',
         'views/res_company_view.xml',
    ],
    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: