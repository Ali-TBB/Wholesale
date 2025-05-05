# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError


class SaleType(models.Model):
    """
    Sale Type Model to manage different sale types for products.
    This model allows the association of a sale type with a product and its quantity.
    """

    _name = 'sale.type'
    _description = 'Sale Type'
    name = fields.Char(string='Type Name', required=True)
    quantity = fields.Integer(string='Quantity', default=1)
    description = fields.Char(string='Description')
    is_default = fields.Boolean(string='Is Default Type')
    is_protected = fields.Boolean(string='Protected Type', default=False)


    def name_get(self):
        """
        Override the name_get method to display the sale type name with quantity (eg: Unit(1) ).
        This method is used to customize the display name of the sale type in selection fields.
        """
        result = []
        for record in self:
            name = f"{record.name} ({record.quantity})"
            result.append((record.id, name))
        return result

    @api.onchange('is_default', 'is_protected', 'name', 'quantity')
    def _check_protected_fields(self):
        """
        Check if the protected fields are being modified.
        If so, raise a UserError to prevent the modification.
        This method is triggered when the user tries to change the values of protected fields.
        """

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


class SaleTypeWizard(models.TransientModel):
    """
    Wizard to change the sale type for selected products.
    This wizard allows the user to select multiple products and assign a new sale type to them.
    """

    _name = 'sale.type.wizard'
    _description = 'Wizard to Change Sale Type for Products'


    product_ids = fields.Many2many('product.template', string="Products")
    sale_type_id = fields.Many2one('sale.type', string="Sale Type", required=True)


    def apply_sale_type(self):
        """
        Apply the selected sale type to the selected products.
        This method is triggered when the user clicks the "Apply" button in the wizard.
        It updates the sale type for all selected products and closes the wizard.
        """

        for product in self.product_ids:
            product.sale_type_id = self.sale_type_id.id

    @api.model
    def default_get(self, fields):
        """
        Override the default_get method to pre-fill the product_ids field with the selected products.
        This method is called when the wizard is opened, and it retrieves the active_ids from the context.
        """
        
        res = super().default_get(fields)
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            res['product_ids'] = [(6, 0, active_ids)]
        return res
