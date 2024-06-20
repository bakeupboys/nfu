# -*- coding: utf-8 -*-
from odoo.http import request
from odoo import fields, http

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleMinMax(WebsiteSale):

    @http.route()
    def cart_update(self, *args, min_qty=None, max_qty=None, **kw):
        """ Override to parse to datetime optional pickup and return dates.
        """
        product_uom_min_qty = fields.Float(min_qty)
        product_uom_max_qty = fields.Float(max_qty)
        return super().cart_update(*args,  min_qty=product_uom_min_qty, max_qty=product_uom_max_qty, **kw)