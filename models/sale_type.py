# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError
from .debug_utils import print_deb


class SaleType(models.Model):
    _name = 'sale.type'
    _description = 'Sale Type'
    name = fields.Char(string='Type Name', required=True)
    quantity = fields.Integer(string='Quantity', default=1)
    description = fields.Char(string='Description')
    is_default = fields.Boolean(string='Is Default Type')
    is_protected = fields.Boolean(string='Protected Type', default=False)


    @api.onchange('is_default', 'is_protected', 'name', 'quantity')
    def _check_protected_fields(self):
        for record in self:
            if record.is_protected and record._origin.is_protected:
                protected_fields = ['is_default', 'is_protected', 'name', 'quantity']
                changed_fields = [
                    field for field in protected_fields
                    if record[field] != record._origin[field]
                ]
                if changed_fields:
                    raise UserError(_(
                        "Protected system types cannot be modified. "
                        "Attempted to change: %s"
                    ) % ", ".join(changed_fields))

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.name} ({record.quantity})"
            result.append((record.id, name))
        return result

from odoo import models, fields

class SaleTypeWizard(models.TransientModel):
    _name = 'sale.type.wizard'
    _description = 'Wizard to Change Sale Type for Products'

    product_ids = fields.Many2many('product.template', string="Products")
    sale_type_id = fields.Many2one('sale.type', string="Sale Type", required=True)

    def apply_sale_type(self):
        for product in self.product_ids:
            product.sale_type_id = self.sale_type_id.id

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            res['product_ids'] = [(6, 0, active_ids)]
        return res
