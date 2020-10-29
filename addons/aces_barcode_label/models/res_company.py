# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013-Present Acespritech Solutions Pvt. Ltd. (<http://acespritech.com>).
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

from openerp import api, fields, models, _
from openerp.exceptions import Warning


class res_company(models.Model):
    _inherit = 'res.company'

    label_height = fields.Float(string="Height", required=True, default=30)
    label_width = fields.Float(string="Width", required=True, default=43)
    label_currency_id = fields.Many2one('res.currency', string="Currency")
    label_currency_position = fields.Selection([('before', 'Before'),
                                          ('after', 'After')], string="Currency Position", default='after')
    label_disp_height = fields.Float(string="Display Height (px)", required=True, default=30)
    label_disp_width = fields.Float(string="Display Width (px)", required=True, default=120)
    label_barcode_type = fields.Selection([('Codabar', 'Codabar'), ('Code11', 'Code11'),
                                    ('Code128', 'Code128'), ('EAN13', 'EAN13'),
                                    ('Extended39', 'Extended39'), ('EAN8', 'EAN8'),
                                    ('Extended93', 'Extended93'), ('USPS_4State', 'USPS_4State'),
                                    ('I2of5', 'I2of5'), ('UPCA', 'UPCA'),
                                    ('QR', 'QR')],
                                   string='Type', default='EAN13')
    label_field_lines = fields.One2many('label.field.lines', 'company_id', string="Fields")


class label_field_lines(models.Model):
    _name = 'label.field.lines'

    text_margin_top = fields.Integer(string="Text Margin Top", default=5)
    font_size = fields.Integer(string="Font Size", default=10)
    font_color = fields.Selection([('black', 'Black'), ('blue', 'Blue'),
                                   ('cyan', 'Cyan'), ('gray', 'Gray'),
                                   ('green', 'Green'), ('lime', 'Lime'),
                                   ('maroon', 'Maroon'), ('pink', 'Pink'),
                                   ('purple', 'Purple'), ('red', 'Red'),
                                   ('yellow', 'Yellow')], string="Font Color", default='black')
    sequence = fields.Selection([(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], string="Sequence")
    name = fields.Selection([('default_code', 'Internal Reference'),
                             ('name', 'Product Name'),
                             ('lst_price', 'Sale Price'),
                             ('ean13', 'EAN13 Barcode'),
                             ('company_id', 'Company')], string="Name")
    company_id = fields.Many2one('res.company', string="Barcode Label ID")

    @api.model
    def create(self, vals):
        res = super(label_field_lines, self).create(vals)
        if res:
            search_lines = self.search([('id', '!=', res.id), ('company_id', '=', res.company_id.id)])
            for line in search_lines:
                if (line.sequence == res.sequence) or (line.name == res.name):
                    raise Warning(_('Sequence and field name cannot repeated.'))
        return res

    @api.multi
    def write(self, vals):
        res = super(label_field_lines, self).write(vals)
        for each in self:
            if res:
                search_lines = self.search([('id', '!=', each.id), ('company_id', '=', each.company_id.id)])
                for line in search_lines:
                    if (line.sequence == each.sequence) or (line.name == each.name):
                        raise Warning(_('Sequence and field name cannot repeated.'))
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: