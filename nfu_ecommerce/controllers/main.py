from odoo import fields, http
from odoo.http import request
from odoo.tools import lazy

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleMinMax(WebsiteSale):
    @http.route()
    def cart_update(self, *args, ordered_qty=None, max_qty=None, **kw):
        """Override to get ordered_qty and max_qty from the product."""
        product_uom_ordered_qty = fields.Float(ordered_qty)
        product_uom_max_qty = fields.Float(max_qty)
        return super().cart_update(
            *args,
            ordered_qty=product_uom_ordered_qty,
            max_qty=product_uom_max_qty,
            **kw
        )


class WebsiteSale(WebsiteSale):
    def _get_additional_shop_values(self, values):
        new_values = super()._get_additional_shop_values(values)
        new_values["open_packagings"] = (
            True if request.httprequest.args.get("open_packagings") else False
        )
        # ToDo: Add batch qtys if open batch
        batch = request.website.sale_get_order(force_create=True).batch_id
        batch_products = batch.product_ids.filtered(lambda p: p.product_packaging_id)
        packaging_info = {}
        for product in (
            values.get("products").sudo().filtered(lambda p: p.packaging_ids)
        ):
            batch_product = batch_products.filtered(
                lambda p: p.product_template_id == product
            )
            if batch_product:
                batch_product = batch_product[0]
                state_color = batch_product.get_state_color()
                if state_color == "inherit":
                    state_color = "green"
                packaging_info[product.id] = {
                    "state_color": state_color,
                    "open_qty": batch_product.open_packaging_qty,
                    "open_max_qty": batch_product.open_packaging_max_qty,
                    "package_qty": batch_product.product_packaging_qty,
                }
        new_values["packaging_info"] = packaging_info
        new_values["get_product_packagings"] = lambda product: lazy(
            lambda: packaging_info.get(product.id, False)
        )
        return new_values

    def _prepare_product_values(self, product, category, search, **kwargs):
        new_values = super()._prepare_product_values(
            product, category, search, **kwargs
        )
        batch = request.website.sale_get_order(force_create=True).batch_id
        batch_product = batch.product_ids.filtered(
            lambda p: p.product_template_id == product and p.product_packaging_id
        )
        packaging_info = {}
        if batch_product:
            batch_product = batch_product[0]
            state_color = batch_product.get_state_color()
            packaging_info = {
                "state_color": state_color,
                "open_qty": batch_product.open_packaging_qty,
                "open_max_qty": batch_product.open_packaging_max_qty,
                "package_qty": batch_product.product_packaging_qty,
            }
        new_values["packaging_info"] = packaging_info
        return new_values

    def _get_search_order(self, post):
        # is_published is company_dependent and has no DB column, so it cannot
        # be used in ORDER BY. The shop domain already filters published products,
        # so dropping it from the sort has no visible effect for visitors.
        order = (
            post.get("order")
            or request.env["website"].get_current_website().shop_default_sort
        )
        return "%s, id desc" % order

    def _get_search_options(
        self,
        category=None,
        attrib_values=None,
        pricelist=None,
        min_price=0.0,
        max_price=0.0,
        conversion_rate=1,
        **post
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
    def shop(
        self,
        page=0,
        category=None,
        search="",
        min_price=0.0,
        max_price=0.0,
        ppg=False,
        **post
    ):
        open_packages = bool(post.get("open_packagings"))
        if open_packages:
            batch = request.website.sale_get_order(force_create=True).batch_id
            open_product_ids = (
                batch.product_ids.filtered(lambda p: p.open_packaging_qty > 0)
                .mapped("product_template_id")
                .ids
            )
            post["open_product_ids"] = open_product_ids
        else:
            post["open_product_ids"] = None
        res = super().shop(
            page=page,
            category=category,
            search=search,
            min_price=min_price,
            max_price=max_price,
            ppg=ppg,
            **post
        )
        return res

    # ToDo: add qntitiy do confiuration modal
    # def show_advanced_configurator(self, product_id, variant_values, pricelist_id, **kw):
    #     batch = request.website.sale_get_order(force_create=True).batch_id
    #     kw['custom_attribute'] = {'batch_id': batch.id}
    #     return super().show_advanced_configurator(product_id, variant_values, pricelist_id, **kw)
