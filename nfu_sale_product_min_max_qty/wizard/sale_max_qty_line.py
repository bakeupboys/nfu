from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleMaxQtyLine(models.TransientModel):
    """
    Lines to shown in Wizard
    """

    _name = "sale.max.qty.line"
    _description = "Max qty Sale Order Lines"

    name = fields.Char()
    sale_max_qty_chooser = fields.Many2one("sale.max.qty.chooser")
    qty = fields.Float()
    max_qty = fields.Float(related="sale_line_id.product_uom_max_qty")
    packaging_size = fields.Float(compute="_compute_packaging_size")
    quantity_fits_packaging = fields.Boolean(compute="_compute_quantity_fits_packaging")
    total_quantity = fields.Float(compute="_compute_quantity_fits_packaging")

    sale_line_id = fields.Many2one("sale.order.line")
    product_id = fields.Many2one(related="sale_line_id.product_id", store=True)
    reset_to_draft = fields.Boolean()

    def _compute_packaging_size(self):
        for max_qty_line in self:
            max_qty_line.packaging_size = min(
                max_qty_line.sale_line_id.product_id.packaging_ids.mapped("qty"), default=1.0
            )

    @api.onchange("qty")
    def _compute_quantity_fits_packaging(self):
        for max_qty_line in self:
            order_lines = max_qty_line.sale_max_qty_chooser.sale_max_qty_ids.filtered(
                lambda line: line.sale_line_id.product_id == max_qty_line.product_id
            )
            max_qty_line.total_quantity = sum(order_lines.mapped("qty"))
            max_qty_line.quantity_fits_packaging = max_qty_line.total_quantity % max_qty_line.packaging_size == 0
            # for order_line in order_lines:
            # order_line.quantity_fits_packaging = max_qty_line.quantity_fits_packaging

    @api.constrains("qty")
    def _check_product_uom_qty(self):
        for max_qty_line in self:
            if max_qty_line.max_qty != 0 and max_qty_line.qty > max_qty_line.max_qty:
                raise UserError(_("The quantity must be less than or equal to the maximum quantity."))
