from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_nfu_packaging(self):
        self.ensure_one()
        if self.packaging_ids:
            return self.packaging_ids[0]
        return False
