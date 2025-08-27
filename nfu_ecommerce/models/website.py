from odoo import fields, models
from odoo.http import request


class Website(models.Model):
    _inherit = "website"

    credit_warning_level = fields.Monetary(
        string="Credit Warning",
        readonly=False,
        help="When the credit of a customer is lower than the warning level the credit is shown in red on the website.",
    )
    avoid_depts = fields.Boolean(string="Avoid depths")

    def sale_get_order(self, force_create=False, update_pricelist=False):
        """Override to clean sale_order_id if so belongs to another website"""
        self.ensure_one()

        self = self.with_company(self.company_id)
        SaleOrder = self.env["sale.order"].sudo()

        sale_order_id = request.session.get("sale_order_id")

        if sale_order_id:
            sale_order = SaleOrder.browse(sale_order_id).exists()
            if sale_order and sale_order.website_id != self:
                request.session.pop("sale_order_id")

        return super().sale_get_order(
            force_create=force_create, update_pricelist=update_pricelist
        )
