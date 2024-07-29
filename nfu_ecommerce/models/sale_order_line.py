from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def compute_open_packages(self):
        self.ensure_one()
        open_qty = self.batch_uom_qty % self.product_packaging_id.qty
        return open_qty
