from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    balance = fields.Monetary(compute="_compute_balance")
    updated_balance = fields.Monetary(compute="_compute_updated_balance")

    def _compute_balance(self):
        for order in self:
            order.balance = -order.partner_id.commercial_partner_id.credit

    @api.depends("amount_total")
    def _compute_updated_balance(self):
        for order in self:
            order.updated_balance = order.balance - (
                order.amount_total / order.currency_rate
            )

    @api.constrains("amount_total")
    def _check_amount_total(self):
        for order in self:
            if order.state != "draft" or not order.website_id:
                continue
            if order.website_id.avoid_depts and order.updated_balance < 0:
                raise ValidationError(_("You don't have enough credit."))

    def _prepare_order_line_values(
        self,
        product_id,
        quantity,
        linked_line_id=False,
        no_variant_attribute_values=None,
        product_custom_attribute_values=None,
        **kwargs
    ):
        values = super()._prepare_order_line_values(
            product_id,
            quantity,
            linked_line_id=linked_line_id,
            no_variant_attribute_values=no_variant_attribute_values,
            product_custom_attribute_values=product_custom_attribute_values,
            **kwargs
        )
        max_qty = float(kwargs.get("max_qty")) if kwargs.get("max_qty") else quantity
        values.update(
            {
                "product_uom_ordered_qty": quantity,
                "product_uom_max_qty": max_qty,
            }
        )
        return values

    def _prepare_order_line_update_values(
        self, order_line, quantity, linked_line_id=False, **kwargs
    ):
        values = super()._prepare_order_line_update_values(
            order_line, quantity, linked_line_id=linked_line_id, **kwargs
        )
        max_qty = kwargs.get("max_qty", quantity)
        if quantity != order_line.product_uom_ordered_qty:
            values["product_uom_ordered_qty"] = quantity
        if max_qty and max_qty != order_line.product_uom_max_qty:
            values["product_uom_max_qty"] = max_qty

        return values

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        for order in orders:
            if order.website_id:
                order.action_add_to_batch()
        return orders
