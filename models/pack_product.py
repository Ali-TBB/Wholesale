from odoo import api, fields, models


class PackProduct(models.Model):
    _name = 'pack.product'
    _description = 'Pack Product'

    name = fields.Char(string='Pack Name', required=True)
    product_ids = fields.Many2one('product.template', string='Product', required=True)
