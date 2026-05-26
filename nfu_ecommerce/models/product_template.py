from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_published = fields.Boolean(
        copy=False,
        default=lambda self: self._default_is_published(),
        index=True,
        company_dependent=True,  # added
    )

    def action_publish_on_website(self):
        for product in self:
            product.is_published = True

    def action_unpublish_on_website(self):
        for product in self:
            product.is_published = False

    def _search_get_detail(self, website, order, options):
        # Pass attrib_values as empty so the parent builds no attribute filter,
        # then add one condition per value to enforce AND semantics.
        attrib_values = options.get("attrib_values")
        patched_options = dict(options, attrib_values=[]) if attrib_values else options
        search_details = super()._search_get_detail(website, order, patched_options)
        open_product_ids = options.get("open_product_ids")
        domain = search_details["base_domain"]
        if open_product_ids is not None:
            domain.append([("id", "in", tuple(open_product_ids))])
        if attrib_values:
            for value in attrib_values:
                domain.append([("attribute_line_ids.value_ids", "in", [value[1]])])
        return search_details
