# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    """
    Sale Order Line Model to manage sale order lines with product and sale type.
    This model allows the association of a product with a specific sale type and quantity.
    """

    _inherit = "sale.order.line"


    sale_type_id = fields.Many2one(
        'sale.type',
        string='Selling Type',
        default= lambda self: self._compute_sale_type_id(),
        store=True,
        readonly=False,  # Important to allow manual override
        help="Selling type inherited from product or manually selected"
    )
    quantity_of_type = fields.Float(string='Quantity Per Type', default=1, required=True)

    def _trigger_price_recalculation(self):
        """Helper method to force price updates"""
        # Update unit price
        self.product_uom_change()
        # Update taxes
        self._compute_tax_id()
        # Update subtotal
        self._compute_amount()
        # Force UI update
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    @api.onchange('product_id')
    def _compute_sale_type_id(self):
        if self.display_type:
            return
        for line in self:
            if line.product_id:
                if line.product_id.product_tmpl_id.sale_type_id:
                    line.sale_type_id = line.product_id.product_tmpl_id.sale_type_id
                else:
                    # Default to the first sale type if none is set
                    default_sale_type = self.env['sale.type'].search([], limit=1)
                    line.sale_type_id = default_sale_type.id if default_sale_type else False
            else:
                line.sale_type_id = False
            self._trigger_price_recalculation()

    @api.onchange('sale_type_id', 'quantity_of_type')
    def _onchange_sale_type(self):
        """Handle sale type changes with quantity conversion"""
        if self.sale_type_id and self.product_id:
            # Convert quantity when switching types
            self.product_uom_qty = self.sale_type_id.quantity * self.quantity_of_type

            self._trigger_price_recalculation()

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get('is_pack'):
            # You can create a dummy pack product or open a wizard
            pack_product = self.env['pack.product'].search([], limit=1)
            if pack_product:
                res.update({
                    'name': pack_product.name,
                    # Optional: set a flag or custom field like is_pack=True
                })
        return res


class SaleOrder(models.Model):
    """
    Sale Order Model to manage sale orders with pack product functionality.
    This model allows the association of a pack product with a sale order and its lines.
    """

    _inherit = 'sale.order'


    def action_open_pack_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Add Pack Product',
            'res_model': 'pack.product.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id,
            },
        }
