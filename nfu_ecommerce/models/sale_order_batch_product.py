from odoo import models


class SaleOrderBatchProduct(models.Model):
    _inherit = "sale.order.batch.product"

    def get_state_color(self):
        self.ensure_one()
        if self.open_packaging_state == "open":
            return "red"
        elif self.open_packaging_state == "last_open":
            return "orange"
        return "inherit"
