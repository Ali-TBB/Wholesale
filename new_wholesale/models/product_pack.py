from odoo import models, fields, api

class ProductPackLine(models.Model):
    _name = 'product.pack.line'
    _description = 'Product Pack Component'
    _order = 'sequence,id'

    pack_product_id = fields.Many2one(
        'product.template',
        string='Pack Product',
        required=True,
        ondelete='cascade'
    )
    component_id = fields.Many2one(
        'product.template',
        string='Component',
        required=True,
        # domain="[('id', '!=', parent.pack_product_id)]"  # Changed domain syntax
    )
    quantity = fields.Float(
        string='Quantity',
        required=True,
        default=1.0
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        related='component_id.uom_id',
        readonly=True
    )
