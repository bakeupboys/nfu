from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_sale_order_line_multiline_description_sale(self):
        """Skipping the variant/custom attribute information on sale order line."""
        self.ensure_one()
        if not self.product_id:
            return super()._get_sale_order_line_multiline_description_sale()
        return self.product_id.get_product_multiline_description_sale()
