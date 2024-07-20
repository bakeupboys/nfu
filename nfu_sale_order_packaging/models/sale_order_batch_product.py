from odoo import api, models


class SaleOrderBatchProduct(models.Model):
    _inherit = "sale.order.batch.product"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:

            if vals.get("product_id") and not vals.get("product_packaging_id"):
                product_id = vals.get("product_id")
                packaging = self.env["product.packaging"].search([("product_id", "=", product_id)], limit=1)
                vals["product_packaging_id"] = packaging.id
        return super().create(vals_list)
