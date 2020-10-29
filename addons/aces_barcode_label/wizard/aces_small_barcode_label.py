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

from openerp import models, fields, api, _
from openerp.exceptions import Warning


class aces_small_barcode_label(models.TransientModel):
    _name = 'aces.small.barcode.label'

    @api.model
    def default_get(self, fields_list):
        prod_list = []
        field_lines = []
        res = super(aces_small_barcode_label, self).default_get(fields_list)
        if self._context.get('active_ids'):
            for product in self._context.get('active_ids'):
                prod_list.append((0, 0, {'product_id': product, 'qty': 1}))
        res['product_lines'] = prod_list
        company_id = self.env['res.users'].browse([self._uid]).company_id
        if company_id:
            for field_line in company_id.label_field_lines:
                field_lines.append((0, 0, {
                                    'text_margin_top': field_line.text_margin_top,
                                    'font_size': field_line.font_size,
                                    'font_color' :field_line.font_color,
                                    'sequence':field_line.sequence,
                                    'name':field_line.name,
                                }))
            res['barcode_type'] = company_id.label_barcode_type
            res['currency_id'] = company_id.label_currency_id.id
            res['currency_position'] = company_id.label_currency_position
            res['disp_height'] = company_id.label_disp_height
            res['disp_width'] = company_id.label_disp_width
            res['height'] = company_id.label_height
            res['width'] = company_id.label_width
            res['field_lines'] = field_lines
        return res

    @api.multi
    def _get_currency(self):
        return self.env['res.users'].browse([self._uid]).company_id.currency_id

    @api.model
    def _get_report_paperformat_id(self):
        xml_id = self.env['ir.actions.report.xml'].search([('report_name', '=',
                                                        'aces_barcode_label.product_barcode_report_template')])
        if not xml_id or not xml_id.paperformat_id:
            raise Warning('Someone has deleted the reference paperformat of report.Please Update the module!')
        return xml_id.paperformat_id.id

    paper_format_id = fields.Many2one('report.paperformat', string="Paper Format", default=_get_report_paperformat_id)
    height = fields.Float(string="Height", required=True, default=30)
    width = fields.Float(string="Width", required=True, default=43)
    currency_id = fields.Many2one('res.currency', string="Currency", default=_get_currency)
    currency_position = fields.Selection([('before', 'Before'),
                                          ('after', 'After')], string="Currency Position", default='after')
    disp_height = fields.Float(string="Display Height (px)", required=True, default=30)
    disp_width = fields.Float(string="Display Width (px)", required=True, default=120)
    barcode_type = fields.Selection([('Codabar', 'Codabar'), ('Code11', 'Code11'),
                                    ('Code128', 'Code128'), ('EAN13', 'EAN13'),
                                    ('Extended39', 'Extended39'), ('EAN8', 'EAN8'),
                                    ('Extended93', 'Extended93'), ('USPS_4State', 'USPS_4State'),
                                    ('I2of5', 'I2of5'), ('UPCA', 'UPCA'),
                                    ('QR', 'QR')],
                                   string='Type', default='EAN13')
    field_lines = fields.One2many('aces.small.barcode.label.line', 'barcode_label_id', string="Fields")
    product_lines = fields.One2many('aces.small.product.label.qty', 'barcode_label_id', string="Product List")

    @api.multi
    def action_call_report(self):
        line_seq = []
        line_name = []
        if self.height <= 0.0 or self.width <= 0.0:
            raise Warning(_("Label height and width should be greater than zero(0)."))
        if self.barcode_type and (self.disp_height <= 0 or self.disp_width <= 0):
            raise Warning(_("Barcode Height and width should be greater than zero(0)."))
        if not self.field_lines:
            raise Warning(_("Please select any one field to print in label."))
        for line in self.field_lines:
            if line.font_size <= 0 and line.name != 'ean13':
                raise Warning(_("Font Size Should be greater than zero(0) for text fields."))
            if line.name == 'ean13' and (not self.barcode_type or self.disp_height <= 0.0 or self.disp_width <= 0.0):
                raise Warning(_("To print barcode enter appropriate data in barcode type, display height and width fields."))
            if not line.sequence or not line.name:
                raise Warning(_("Sequence and fields name can not be empty."))
            if line.sequence in line_seq or line.name in line_name:
                raise Warning(_("Sequence and field name cannot repeated."))
            line_seq.append(line.sequence)
            line_name.append(line.name)
        if 'lst_price' in line_name and self.currency_id and not self.currency_position:
            raise Warning(_("Please, select currency position to display currency symbol."))
        if 'barcode' in line_name:
            if not [product.product_id.ean13 for product in self.product_lines if product.product_id.ean13]:
                raise Warning(_("You have selected barcode to print, but none of product(s) contain(s) barcode."))
        if sum([p.qty for p in self.product_lines]) <= 0:
            raise Warning(_("Please, enter product quantity to print no. of labels."))
        self.paper_format_id.write({
            'page_width': self.width,
            'page_height': self.height
        })
        data = self.read()[0]
        datas = {
            'ids': self._ids,
            'model': 'aces.small.barcode.label',
            'form': data
        }
        return  self.env['report'].get_action(self, 'aces_barcode_label.product_barcode_report_template', data=datas)


class aces_small_barcode_label_line(models.TransientModel):
    _name = 'aces.small.barcode.label.line'

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
    barcode_label_id = fields.Many2one('aces.small.barcode.label', string="Barcode Label ID")


class aces_small_barcode_label_line(models.TransientModel):
    _name = 'aces.small.product.label.qty'

    product_id = fields.Many2one('product.product', string="Product(s)", required=True)
    qty = fields.Integer(string="Quantity", default=1)
    barcode_label_id = fields.Many2one('aces.small.barcode.label', string="Barcode Label ID")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
