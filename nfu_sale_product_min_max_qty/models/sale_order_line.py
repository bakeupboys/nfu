from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_uom_min_qty = fields.Float(string="Min qty.", digits="Product Unit of Measure")
    product_uom_max_qty = fields.Float(string="Max qty.", digits="Product Unit of Measure")

    @api.constrains("product_uom_qty", "product_uom_max_qty")
    def _check_product_uom_qty(self):
        for record in self:
            if record.product_uom_max_qty != 0 and record.product_uom_qty > record.product_uom_max_qty:
                raise UserError(_("The quantity must be less than or equal to the maximum quantity."))
