from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_sale_order_line_multiline_description_sale(self):
        """Build the description from the product name (and internal reference)
        plus its sales description, but without any variant information.

        The standard description is built from the product ``display_name``,
        which appends the variant attribute combination (e.g. ``(Large)``), and
        from the no-variant/custom attribute lines. For the NFU project none of
        that variant information may appear on the order line, while the
        internal reference and the sales description are kept.
        """
        self.ensure_one()
        product = self.product_id
        if not product:
            return super()._get_sale_order_line_multiline_description_sale()
        name = product.name
        if product.default_code and self.env.context.get("display_default_code", True):
            name = "[%s] %s" % (product.default_code, name)
        if product.description_sale:
            name += "\n" + product.description_sale
        return name
