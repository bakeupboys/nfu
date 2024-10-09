from odoo import fields, models
from odoo.tools import float_is_zero, float_round


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    open_qty = fields.Float(compute="_compute_open_qty")

    def _compute_open_qty(self):
        for line in self:
            if line.product_packaging_id:
                precision_rounding = line.product_id.uom_id.rounding
                precision_digits = len(str(precision_rounding).split(".")[1])
                qty_of_last_pack = float_round(
                    line.batch_uom_qty % line.product_packaging_id.qty, precision_rounding=precision_rounding
                )
                if not float_is_zero(qty_of_last_pack, precision_rounding=precision_rounding):
                    line.open_qty = round(line.product_packaging_id.qty - qty_of_last_pack, precision_digits)
                else:
                    line.open_qty = 0.0
            else:
                line.open_qty = 0.0
