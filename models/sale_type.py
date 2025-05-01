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

    # def unlink(self):
    #     protected_types = self.filtered(lambda st: st.is_protected)
    #     if protected_types:
    #         raise UserError(_(
    #             "You cannot delete protected sale types like '%s'. "
    #             "These are system default types."
    #         ) % protected_types[0].name)
    #     return super(SaleType, self).unlink()

    @api.constrains('is_default', 'is_protected', 'name', 'quantity')
    def _check_protected_fields(self):
        for record in self:
            if record.is_protected and record._origin.is_protected:
                protected_fields = ['is_default', 'is_protected', 'name', 'quantity']
                changed_fields = [
                    field for field in protected_fields
                    if record[field] != record._origin[field]
                ]
                print_deb(" this is a protected field", changed_fields)
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

