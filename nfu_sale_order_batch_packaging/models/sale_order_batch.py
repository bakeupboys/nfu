from odoo import models


class SaleOrderBatch(models.Model):
    _inherit = "sale.order.batch"

    def action_recompute_products(self):
        for batch in self:
            batch.product_ids.unlink()
            for line in batch.sale_order_line_ids:
                line._update_batch_product()
