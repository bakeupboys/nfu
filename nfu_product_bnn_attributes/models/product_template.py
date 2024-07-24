from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    manufacturer_abbr = fields.Char(string="Manufacturer Abbreviation")
    # Should be moved to product.product at some point
    additional_information = fields.Char()
    quality = fields.Char()
    origin = fields.Char()
    packaging_qty = fields.Float(string="Packaging Quantity")
    packaging_name = fields.Char()

    @api.depends("packaging_qty", "packaging_name")
    def generate_packaging_from_bnn(self):
        for product in self:
            qty = product.packaging_qty
            name = product.packaging_name
            if qty and name:
                packagings = (
                    self.env["product.packaging"]
                    .search([("product_id", "=", product.id)])
                    .filtered(lambda p: p.qty == qty)
                )
                if packagings:
                    packagings[0].write({"name": name})
                else:
                    self.env["product.packaging"].create({"name": name, "qty": qty, "product_id": product.id})

    def write(self, vals):
        res = super().write(vals)
        if vals.get("packaging_qty"):
            for product in self:
                qty = vals.get("packaging_qty")
                name = vals.get("packaging_name") if vals.get("packaging_name") else product.packaging_name
                if qty and name:
                    packagings = (
                        self.env["product.packaging"]
                        .search([("product_id", "=", product.id)])
                        .filtered(lambda p: p.qty == qty)
                    )
                    if packagings:
                        packagings[0].write({"name": name})
                    else:
                        self.env["product.packaging"].create(
                            {"name": name, "qty": qty, "product_id": product.id, "sales": True}
                        )
        return res
