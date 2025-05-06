from odoo import api, models, fields


class PackProduct(models.Model):
    _name="pack.product"
    _description = "Model to manage pack products"


    name = fields.Char(string="Pack Name", required=True)
    line_ids = fields.One2many('pack.line', 'pack_id', string="Products")
    def add_product_to_order(self):
        """
        Add the selected pack product to the sale order.
        This method creates sale order lines for each product in the pack and calculates the total price.
        It also creates a line section for the pack in the sale order.
        """
        # Check if the pack product and sale order are set
        if not self.sale_order_id or not self.pack_product:
            return

        order = self.sale_order_id
        pack = self.pack_product

        order.order_line.create({
            'order_id': order.id,
            'display_type': 'line_section',
            'name': f'Pack : {pack.name}',
        })

        for line in pack.line_ids:
            if not line.product_id:
                continue  # skip empty product lines
            order.order_line.create({
                'order_id': order.id,
                'product_id': line.product_id.id,
                'sale_type_id': line.sale_type_id.id or line.product_id.product_tmpl_id.sale_type_id.id,
                'quantity_of_type': line.quantity,
                'product_uom_qty': line.quantity * line.sale_type_id.quantity or 1.0,
                'name': f"{line.product_id.display_name}",
            })

        order.order_line.create({
            'order_id': order.id,
            'display_type': 'line_section',
            'name': ' ' * 130 + f'Total price of Pack : {pack.total_price}',
        })

class PackLine(models.Model):
    _name = "pack.line"


    pack_id = fields.Many2one('pack.product', ondelete="cascade", required=True)
    product_id = fields.Many2one('product.template')
    quantity = fields.Integer(string="Quantity")
    sale_type_id = fields.Many2one('sale.type', string="Sale Type", )

