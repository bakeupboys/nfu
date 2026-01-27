from odoo import fields, models

from odoo.addons.data_nature_importer.utils import get_datanature_metadata


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # TODO: Remove as soon as data_nature thumbnails work
    image_1920 = fields.Image(verify_resolution=False)

    manufacturer_abbr = fields.Char(string="Manufacturer Abbreviation")
    # Should be moved to product.product at some point
    additional_information = fields.Char()
    quality = fields.Char()
    origin = fields.Char()
    packaging_qty = fields.Float(string="Packaging Quantity")
    packaging_name = fields.Char()
    gtin_article = fields.Char(string="Article GTIN")

    def _get_dn_metadata(self):
        self.ensure_one()
        if self.gtin_article:
            metadata = get_datanature_metadata(self, self.gtin_article)
            if metadata:
                return metadata[0]
        return super()._get_dn_metadata()

    def write(self, vals):
        res = super().write(vals)
        if vals.get("packaging_qty") or vals.get("packaging_name"):
            for product in self:
                qty = vals.get("packaging_qty") or product.packaging_qty
                name = vals.get("packaging_name") or product.packaging_name
                product_products = self.env["product.product"].search(
                    [("product_tmpl_id", "=", product.id)]
                )
                if qty and name:
                    for product_product in product_products:
                        packagings = self.env["product.packaging"].search(
                            [("product_id", "=", product_product.id)], limit=1
                        )
                        if packagings:
                            packagings.write(
                                {
                                    "name": name,
                                    "qty": qty,
                                    "sales": True,
                                    "company_ids": product_product.company_ids.ids,
                                }
                            )
                        else:
                            self.env["product.packaging"].create(
                                {
                                    "name": name,
                                    "qty": qty,
                                    "product_id": product_product.id,
                                    "sales": True,
                                    "company_ids": product_product.company_ids.ids,
                                }
                            )
        return res
