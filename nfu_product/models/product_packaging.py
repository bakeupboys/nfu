from odoo import api, models


class ProductPackaging(models.Model):
    _inherit = ["multi.company.abstract", "product.packaging"]
    _name = "product.packaging"

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for packaging in res:
            product = packaging.product_id
            packaging.company_ids = product.company_ids
        return res
