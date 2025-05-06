from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sale_type_id = fields.Many2one(
        'sale.type',
        string="Sale Type",
        default= lambda self : self._get_default_sale_type_id(),
        required=True
        )

    @api.model
    def _get_default_sale_type_id(self):
        unit_type = self.env['sale.type'].search([('name', '=', 'Unit')], limit=1)
        return unit_type.id