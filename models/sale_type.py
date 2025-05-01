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


class SaleTypeWizard(models.TransientModel):
    _name = 'sale.type.wizard'
    _description = 'Change Sale Type Wizard'
    
    sale_type = fields.Selection(
        [('retail', 'Retail'), ('wholesale', 'Wholesale')],
        string="Sale Type",
        required=True
    )
    product_ids = fields.Many2many(
        'product.template',
        string="Products"
    )
    
    def action_change_sale_type(self):
        self.ensure_one()
        if self.product_ids:
            self.product_ids.write({'sale_type': self.sale_type})
        return {'type': 'ir.actions.act_window_close'}