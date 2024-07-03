from odoo import _, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_min_max_qty_wizard(self):
        """
        Here you need to create the wizzard objects first and then call the wizzard with the newly created id
        """
        sale_max_qty_chooser = self.env["sale.max.qty.chooser"].create({})
        draft_sale_orders = self.filtered(lambda x: x.state == "draft")
        for sale_order in draft_sale_orders:
            sale_order_lines = self.env["sale.order.line"].search([("id", "in", sale_order.order_line.ids)])

            for line in sale_order_lines:
                if not line.display_type:
                    self.env["sale.max.qty.line"].create(
                        {
                            "sale_line_id": line.id,
                            "sale_max_qty_chooser": sale_max_qty_chooser.id,
                            "qty": line.product_uom_qty,
                        }
                    )

        action = {
            "name": _("Min max qty wizard"),
            "type": "ir.actions.act_window",
            "res_model": "sale.max.qty.chooser",
            "view_mode": "form",
            "target": "new",
            "res_id": sale_max_qty_chooser.id,
        }
        return action

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
        values.update({"product_uom_min_qty": quantity, "product_uom_max_qty": kwargs.get("max_qty", quantity)})
        return values

    def _prepare_order_line_update_values(self, order_line, quantity, linked_line_id=False, **kwargs):
        values = super()._prepare_order_line_update_values(
            order_line, quantity, linked_line_id=linked_line_id, **kwargs
        )
        max_qty = kwargs.get("max_qty", quantity)
        if quantity != order_line.product_uom_min_qty:
            values["product_uom_min_qty"] = quantity
        if max_qty and max_qty != order_line.product_uom_max_qty:
            values["product_uom_max_qty"] = max_qty

        return values
