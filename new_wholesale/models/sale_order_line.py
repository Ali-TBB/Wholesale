from odoo import api, models, fields
from .debug_utils import print_deb


class SaleOrderLine(models.Model):
    _inherit="sale.order.line"

    sale_type_id = fields.Many2one('sale.type', string="Sale Type")
    quantity_of_type = fields.Float(string="Quantity of Type")

    is_pack_component = fields.Boolean(string="Is Pack Component", store=True)
    pack_parent_line_id = fields.Many2one('sale.order.line', string="Parent Pack Line")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id.is_pack and not self.env.context.get('skip_pack_creation'):
            # Calculate total pack price
            # total_price = sum(
            #     comp.component_id.list_price * comp.quantity 
            #     for comp in self.product_id.pack_component_ids
            # )

            # Prepare component lines data (won't create them yet)
            component_data = []
            for component in self.product_id.pack_component_ids:
                component_data.append((0, 0, {
                    'order_id': self.order_id.id,
                    'product_id': component.component_id.id,
                    'product_uom_qty': component.quantity * self.product_uom_qty,
                    'price_unit': component.component_id.list_price,
                    'is_pack_component': True,
                    'pack_parent_line_id': self.id,
                    'product_uom': component.component_id.uom_id.id,
                    'tax_id': [(6, 0, component.component_id.taxes_id.ids)]
                }))

            return {
                'value': {
                    'price_unit': self.product_id.pack_price,
                    'price_total': 0.0
                    # 'name': self.product_id.pack_description,
                },
                'domain': {
                    'order_id': [('id', '=', self.order_id.id)]
                }
            }
        elif not self.product_id.is_pack:
            # Clear any existing pack components if product changes to non-pack
            self.env['sale.order.line'].search([
                ('pack_parent_line_id', '=', self.id),
                ('order_id', '=', self.order_id.id)
            ]).unlink()

    @api.model
    def create(self, vals):
        line = super().create(vals)
        if line.product_id.is_pack:
            # Create actual component lines after main line is created
            line._create_pack_components()
        return line

    def write(self, vals):
        res = super().write(vals)
        if 'product_id' in vals:
            for line in self:
                if line.product_id.is_pack:
                    # Remove old components and create new ones
                    self.env['sale.order.line'].search([
                        ('pack_parent_line_id', '=', line.id),
                        ('order_id', '=', line.order_id.id)
                    ]).unlink()
                    line._create_pack_components()
        return res

    def _create_pack_components(self):
        """Create actual pack component lines"""
        self.ensure_one()
        if self.product_id.is_pack:
            for component in self.product_id.pack_component_ids:
                self.env['sale.order.line'].create({
                    'order_id': self.order_id.id,
                    'product_id': component.component_id.id,
                    'product_uom_qty': component.quantity * self.product_uom_qty,
                    'price_unit': component.component_id.list_price,
                    'is_pack_component': True,
                    'pack_parent_line_id': self.id,
                    'product_uom': component.component_id.uom_id.id,
                    'tax_id': [(6, 0, component.component_id.taxes_id.ids)]
                })


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """Override to exclude pack component prices from totals"""
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                if not line.product_id.is_pack:  # Only count non-component lines
                    amount_untaxed += line.price_subtotal
                    amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

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