from odoo import api, models


class ProductPackaging(models.Model):
    _inherit = ["multi.company.abstract", "product.packaging"]
    _name = "product.packaging"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            product = self.env["product.product"].browse(vals.get("product_id"))
            vals["company_ids"] = [(6, 0, product.company_ids.ids)]
        res = super().create(vals_list)
        return res
