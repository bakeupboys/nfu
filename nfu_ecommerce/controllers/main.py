from odoo import fields, http

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleMinMax(WebsiteSale):
    @http.route()
    def cart_update(self, *args, ordered_qty=None, max_qty=None, **kw):
        """Override to get ordered_qty and max_qty from the product."""
        product_uom_ordered_qty = fields.Float(ordered_qty)
        product_uom_max_qty = fields.Float(max_qty)
        return super().cart_update(*args, ordered_qty=product_uom_ordered_qty, max_qty=product_uom_max_qty, **kw)
