from odoo import api, fields, models


class PackProduct(models.Model):
    """
    Pack Product Model to manage product packs.
    This model allows the creation of product packs with multiple products and their respective quantities.
    It also calculates the total price of the pack based on the products and their quantities.
    """

    _name = 'pack.product'
    _description = 'Pack Product'


    name = fields.Char(string='Pack Name', required=True)
    line_ids = fields.One2many('pack.product.line', 'pack_id', string='Pack Lines')
    total_price = fields.Float(string='Total Price', compute='_compute_total_price', store=True)


    @api.depends('line_ids.product_id', 'line_ids.quantity', 'line_ids.sale_type_id.quantity')
    def _compute_total_price(self):
        """
        Compute the total price of the pack based on the products and their quantities.
        This method is triggered when the pack lines are modified or when the pack is created.
        """

        for pack in self:
            total = 0.0
            for line in pack.line_ids:
                if line.product_id and line.sale_type_id:
                    total += line.product_id.lst_price * line.quantity * line.sale_type_id.quantity
            pack.total_price = total


class PackProductLine(models.Model):
    """
    Pack Product Line Model to manage individual products within a pack.
    This model allows the association of a product with a specific pack and its quantity.
    """

    _name = 'pack.product.line'
    _description = 'Pack Product Line'


    pack_id = fields.Many2one('pack.product', string='Pack', ondelete='cascade', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    sale_type_id = fields.Many2one(
        'sale.type',
        string='Selling Type',
        store=True,
        readonly=False,
        help="Selling type inherited from product or manually selected",
        required=True
    )
    quantity = fields.Float(string='Quantity', required=True, default=1.0)


class PackProductWizard(models.TransientModel):
    """
    Wizard to select a pack product and add it to the sale order.
    This wizard allows the user to choose a pack product and automatically adds the products within the pack to the sale order.
    """

    _name = 'pack.product.wizard'
    _description = 'Wizard to Choose Pack Product'


    pack_product = fields.Many2one('pack.product', string="Pack", required=True)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True)


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
