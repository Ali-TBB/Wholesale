from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SaleType(models.Model):
    _name = 'sale.type'
    _description = 'Sale Type'

    name = fields.Char(string="Type Name", required=True)
    quantity = fields.Integer(string="Quantity", required=True)
    is_protected = fields.Boolean(string="Protected", default=False)
    description = fields.Char(string="Description")

    @api.model
    def create_default_sale_type(self):
        if not self.search([('name', '=', 'Unit')]):
            self.create({
                'name': 'Unit',
                'quantity': 1,
                'description': 'Default unit sale type',
                'is_protected': True
            })

    @api.onchange('name', 'quantity', 'is_protected')
    def _check_protected_sale_type(self):
        for record in self:
            if record.is_protected and record._origin.is_protected:
                protected_fields = ['name', 'quantity', 'is_protected']
                changed_fields = [
                    field for field in protected_fields
                    if record[field] != record._origin[field]
                ]
                if changed_fields:
                    raise UserError(_(
                        "Protected system types cannot be modified. "
                        "Attempted to change: %s"
                    ) % ", ".join(changed_fields))

    def unlink(self):
        default_sale_type = self.env['sale.type'].search([('name', '=', 'Unit')], limit=1)

        if not default_sale_type:
            raise UserError(_("Default 'Unit' sale type not found. Cannot proceed."))

        for record in self:
            if record.is_protected:
                raise UserError(_(
                    "You cannot delete a protected sale type: %s"
                ) % record.name)

            # Find all products using this sale type
            products = self.env['product.template'].search([('sale_type_id', '=', record.id)])
            if products:
                products.write({'sale_type_id': default_sale_type.id})

        return super(SaleType, self).unlink()


    def init(self):
        self.create_default_sale_type()

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

class SaleTypeWizard(models.TransientModel):
    _name = "sale.type.wizard"
    _description = "wizard to change sale type of multiple product"

    product_ids = fields.Many2many('product.template', string="Products")
    sale_type_id = fields.Many2one('sale.type', string="Sale Type")


    def apply_sale_type(self):
        if self.product_ids:
            for product in self.product_ids:
                product.sale_type_id = self.sale_type_id.id
    
    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            res['product_ids'] = [(6, 0, active_ids)]
        return res
