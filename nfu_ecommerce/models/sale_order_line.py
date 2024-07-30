from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def compute_open_packages(self):
        self.ensure_one()
        qty_of_last_pack = self.batch_uom_qty % self.product_packaging_id.qty
        open_qty = self.product_packaging_id.qty - qty_of_last_pack
        return open_qty
