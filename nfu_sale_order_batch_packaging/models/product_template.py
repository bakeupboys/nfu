from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_nfu_packaging(self):
        self.ensure_one()
        if self.packaging_ids:
            return self.packaging_ids[0]
        return False
