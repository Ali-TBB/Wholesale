
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    selling_type = fields.Selection(string='Selling Type', selection=[('unit', 'Unit'), ('box', 'Box')])
    qty_per_box = fields.Integer(string='Quantity Per Box')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            # Get values from product template
            self.qty_per_box = self.product_id.product_tmpl_id.qty_per_box or 1
            self.selling_type = self.product_id.product_tmpl_id.selling_type or 'unit'

            # Set initial quantity
            if self.selling_type == 'box':
                self.product_uom_qty = 1  # Start with 1 box

            # Trigger all necessary updates
            self._trigger_price_recalculation()

    @api.onchange('selling_type')
    def _onchange_selling_type(self):
        if self.product_id:
            self.qty_per_box = self.product_id.product_tmpl_id.qty_per_box or 1
            if self.selling_type == 'box':
                self.product_uom_qty = self.qty_per_box
            else:
                self.product_uom_qty = 1
            # Trigger all necessary updates
            self._trigger_price_recalculation()

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