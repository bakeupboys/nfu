from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_published = fields.Boolean(
        copy=False,
        default=lambda self: self._default_is_published(),
        index=True,
        company_dependent=True,
    )

    def action_publish_on_website(self):
        for product in self:
            product.is_published = True

    def action_unpublish_on_website(self):
        for product in self:
            product.is_published = False

    def _search_get_detail(self, website, order, options):
        search_details = super()._search_get_detail(website, order, options)
        open_product_ids = options.get("open_product_ids")
        domain = search_details["base_domain"]
        if open_product_ids is not None:
            domain.append([("id", "in", tuple(open_product_ids))])
        return search_details
