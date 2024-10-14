from odoo import fields, http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleMinMax(WebsiteSale):
    @http.route()
    def cart_update(self, *args, ordered_qty=None, max_qty=None, **kw):
        """Override to get ordered_qty and max_qty from the product."""
        product_uom_ordered_qty = fields.Float(ordered_qty)
        product_uom_max_qty = fields.Float(max_qty)
        return super().cart_update(*args, ordered_qty=product_uom_ordered_qty, max_qty=product_uom_max_qty, **kw)


class WebsiteSale(WebsiteSale):
    def _get_additional_shop_values(self, values):
        new_values = super()._get_additional_shop_values(values)
        new_values["open_packagings"] = True if request.httprequest.args.get("open_packagings") else False
        return new_values

    def _get_search_options(
        self, category=None, attrib_values=None, pricelist=None, min_price=0.0, max_price=0.0, conversion_rate=1, **post
    ):
        res = super()._get_search_options(
            category=category,
            attrib_values=attrib_values,
            pricelist=pricelist,
            min_price=min_price,
            max_price=max_price,
            conversion_rate=conversion_rate,
            **post
        )
        res["open_product_ids"] = post.get("open_product_ids")
        return res

    @http.route(
        [
            "/shop",
            "/shop/page/<int:page>",
            '/shop/category/<model("product.public.category"):category>',
            '/shop/category/<model("product.public.category"):category>/page/<int:page>',
        ],
        type="http",
        auth="public",
        website=True,
    )
    def shop(self, page=0, category=None, search="", min_price=0.0, max_price=0.0, ppg=False, **post):
        open_packages = bool(post.get("open_packagings"))
        if open_packages:
            batch = request.website.sale_get_order(force_create=True).batch_id
            open_product_ids = (
                batch.product_ids.filtered(lambda p: p.open_packaging_qty > 0).mapped("product_template_id").ids
            )
            post["open_product_ids"] = open_product_ids
        else:
            post["open_product_ids"] = None
        res = super().shop(
            page=page, category=category, search=search, min_price=min_price, max_price=max_price, ppg=ppg, **post
        )
        return res
