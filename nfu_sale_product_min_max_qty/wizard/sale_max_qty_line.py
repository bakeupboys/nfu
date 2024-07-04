from odoo import fields, models, api


class SaleMaxQtyLine(models.TransientModel):
    """
    Lines to shown in Wizard
    """

    _name = "sale.max.qty.line"
    _description = "Max qty Sale Order Lines"

    sale_max_qty_chooser = fields.Many2one("sale.max.qty.chooser")
    qty = fields.Float()
    max_qty = fields.Float(related="sale_line_id.product_uom_max_qty")
    packaging_size = fields.Float(compute="_compute_packaging_size")
    quantity_fits_packaging = fields.Boolean(compute='_compute_quantity_fits_packaging')

    sale_line_id = fields.Many2one("sale.order.line")
    product_id = fields.Many2one(related="sale_line_id.product_id")
    reset_to_draft = fields.Boolean()

    def _compute_packaging_size(self):
        for sale_order in self:
            sale_order.packaging_size = min(sale_order.sale_line_id.product_id.packaging_ids.mapped('qty'), default=1.0)

    @api.depends('packaging_size', 'qty')
    def _compute_quantity_fits_packaging(self):
        for sale_order in self:
            order_lines = self.sale_max_qty_chooser.sale_max_qty_ids.filtered(lambda line: line.sale_line_id.product_id == sale_order.product_id)
            total_quantity = sum(order_lines.mapped('qty'))
            sale_order.quantity_fits_packaging = total_quantity % sale_order.packaging_size == 0