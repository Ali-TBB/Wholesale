# -*- coding: utf-8 -*-
from email.policy import default

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    sale_type_id = fields.Many2one(
        'sale.type',
        string='Selling Type',
        default= lambda self: self._compute_sale_type_id(),
        store=True,
        readonly=False,  # Important to allow manual override
        help="Selling type inherited from product or manually selected"
    )
    quantity_of_type = fields.Float(string='Quantity', default=1, required=True)

    @api.onchange('product_id')
    def _compute_sale_type_id(self):
        for line in self:
            if line.product_id:
                line.sale_type_id = line.product_id.product_tmpl_id.sale_type_id
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
