# -*- encoding: utf-8 -*-
##############################################################################
#    Copyright (c) 2012 - Present Acespritech Solutions Pvt. Ltd. All Rights Reserved
#    Author: <info@acespritech.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of the GNU General Public License is available at:
#    <http://www.gnu.org/licenses/gpl.html>.
#
##############################################################################
{
    'name': 'POS Mohas',
    'version': '1.0',
    'category': 'Point of Sale',
    'description': """
This module has multiple features like keyboard shortcut,product load in background,products returns
and pos product serial.
""",
    'author': "Acespritech Solutions Pvt. Ltd.",
    'website': "www.acespritech.com",
    'depends': ['web', 'point_of_sale', 'base','purchase'],
    'data': ['views/pos_mohas.xml',
             'stock/stock_view.xml',
             'pos_order/point_of_sale_view.xml'],
    'demo': [],
    'test': [],
    'qweb': ['static/src/xml/pos_mohas.xml'],
    'installable': True,
    'auto_install': False,
    'post_init_hook': 'set_default_values',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: