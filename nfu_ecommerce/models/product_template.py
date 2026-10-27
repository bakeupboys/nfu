from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_published = fields.Boolean(
        copy=False,
        default=lambda self: self._default_is_published(),
        index=True,
        company_dependent=True,  # added
    )

    # Searchable mirror of is_published. Because is_published is
    # company_dependent it has no column: Odoo resolves a domain leaf on it in
    # Python (ir.property.search_multi) and substitutes the full list of
    # matching ids -- ~18k ids for company 1 here, which turned every webshop
    # search into a ~130 kB statement and caused the Postgres OOM on
    # 2026-10-27. This field answers the same question with one indexed
    # subquery. It exists only to be searched; sale_product_domain swaps the
    # is_published leaf for it.
    nfu_published_for_company = fields.Boolean(
        string="Published for current company",
        compute="_compute_nfu_published_for_company",
        search="_search_nfu_published_for_company",
    )

    def _compute_nfu_published_for_company(self):
        for product in self:
            product.nfu_published_for_company = product.is_published

    def _search_nfu_published_for_company(self, operator, value):
        if operator not in ("=", "!=") or not isinstance(value, bool):
            # Unexpected caller: fall back to the slow but correct original.
            return [("is_published", operator, value)]
        published = value if operator == "=" else not value
        field = self.env["ir.model.fields"]._get("product.template", "is_published")
        # One ir_property row per published product and company; "not
        # published" is the absence of a row. Served by ir_property_unique_index
        # on (fields_id, company_id, res_id).
        subselect = """
            SELECT CAST(split_part(p.res_id, ',', 2) AS INTEGER)
            FROM ir_property p
            WHERE p.fields_id = %s
              AND p.company_id = %s
              AND p.res_id IS NOT NULL
              AND COALESCE(p.value_integer, 0) = 1
        """
        params = [field.id, self.env.company.id]
        return [
            ("id", "inselect" if published else "not inselect", (subselect, params))
        ]

    def _has_no_variant_attributes(self):
        res = super()._has_no_variant_attributes()
        # During a merging cart search, hide no_variant attributes from the
        # "always new line" guard when they all opted into merging.
        if res and self.env.context.get("nfu_merge_no_variant"):
            no_variant_attributes = (
                self.valid_product_template_attribute_line_ids.attribute_id.filtered(
                    lambda a: a.create_variant == "no_variant"
                )
            )
            if no_variant_attributes and all(
                a.nfu_merge_cart_lines for a in no_variant_attributes
            ):
                return False
        return res

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
