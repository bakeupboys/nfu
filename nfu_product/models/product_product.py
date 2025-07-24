from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def write(self, vals):
        if "company_ids" in vals:
            for product in self:
                company_ids = vals.get("company_ids", [])[0][2]
                if company_ids:
                    related_packages = self.env["product.packaging"].search(
                        [("product_id", "=", product.id)]
                    )

                    # First, set the company_ids on packages if not set
                    for package in related_packages:
                        if not package.company_ids:
                            package.company_ids = product.company_ids
                        else:
                            allowed_company_ids = list(
                                set(package.company_ids.ids) & set(company_ids)
                            )
                            if not allowed_company_ids:
                                package.company_ids = [(6, 0, company_ids)]
                            else:
                                package.company_ids = [(6, 0, allowed_company_ids)]
        res = super().write(vals)
        return res
