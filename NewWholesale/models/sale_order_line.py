from odoo import api, models, fields
from .debug_utils import print_deb

class SaleOrderLine(models.Model):
    _inherit="sale.order.line"

    sale_type_id = fields.Many2one('sale.type', string="Sale Type")
    quantity_of_type = fields.Float(string="Quantity of Type")
    product_or_pack_ref = fields.Reference(
        selection=[
            ('product.template', 'Product'),
            ('pack.product', 'Kit')
        ],
        string="Product & Kit",
        required=True,
        )
    is_pack_line = fields.Boolean(string="Is from Pack", default=False)


    @api.onchange('product_or_pack_ref')
    def _onchange_product_or_pack_ref(self):
        """Handle product/pack selection with proper singleton handling"""
        for line in self:
            if not line.product_or_pack_ref:
                line.update({
                    'sale_type_id': False,
                    'name': '',
                    'price_unit': 0.0,
                    'product_id': False,
                    'product_uom_qty': 1.0,
                })
                continue

            ref = line.product_or_pack_ref
            values = {}
            
            if ref._name == 'product.template':
                # Handle regular product selection
                product = ref
                values.update({
                    'product_id': product.product_variant_id.id,
                    'name': product.name,
                    'quantity_of_type': 1.0,
                    'product_uom': product.uom_id.id,
                    'price_unit': product.list_price,
                    'sale_type_id': product.sale_type_id or self.env['sale.type'].search([], limit=1),
                    'is_pack_line': False,
                })

            elif ref._name == 'pack.product':
                # Handle pack selection
                values.update({
                    'name': ref.name,
                    'price_unit': 0.0,
                    'quantity_of_type': 1.0,
                    'product_id': False,
                    'product_uom': False,
                    'sale_type_id': self.env['sale.type'].search([], limit=1),
                    'is_pack_line': False,
                })

            # Update current line with new values
            line.update(values)

            self._onchange_sale_type_and_quantity()
            # Force UI update
            return {
                'value': {
                    'price_unit': line.price_unit,
                    'price_subtotal': line.price_subtotal,
                    'price_tax': line.price_tax,
                    'price_total': line.price_total,
                    **values,
                }
            }


    @api.onchange('sale_type_id', 'quantity_of_type')
    def _onchange_sale_type_and_quantity(self):
        """Handle sale type changes with quantity conversion"""
        if self.sale_type_id and self.product_id:
            # Convert quantity when switching types
            self.product_uom_qty = self.sale_type_id.quantity * self.quantity_of_type

            self._trigger_recalculate_price()


    def _trigger_recalculate_price(self):
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