# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sale_type_id = fields.Many2one(
        'sale.type',
        string='Sale Type',
        # default=lambda self: self._get_default_sale_type_id(),
        help="Select the sale type for this product (e.g., Unit, Box, Pack)"
    )

    # @api.model
    # def _get_default_sale_type_id(self):
    #     """ Return the ID of the 'Unit' sale type as default """
    #     unit_type = self.env['sale.type'].search([('name', '=', 'Unit')], limit=1)
    #     return unit_type.id if unit_type else False
    # def _get_default_sale_order_type_id(self):
    #     """ Return the ID of the 'Unit' sale order as default """
