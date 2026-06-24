from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestSaleOrderLineDescription(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "Test Partner"})

    def _make_order_line(self, product):
        order = self.env["sale.order"].create({"partner_id": self.partner.id})
        return self.env["sale.order.line"].create(
            {"order_id": order.id, "product_id": product.id}
        )

    def test_description_skips_variant_attributes(self):
        """A small and a large baguette (two real variants) keep the product
        name, internal reference and sales description, but never show their
        size attribute value."""
        attribute = self.env["product.attribute"].create(
            {
                "name": "Size",
                "create_variant": "always",
                "value_ids": [
                    (0, 0, {"name": "Small"}),
                    (0, 0, {"name": "Large"}),
                ],
            }
        )
        template = self.env["product.template"].create(
            {
                "name": "Baguette",
                "description_sale": "Crusty loaf",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": attribute.id,
                            "value_ids": [(6, 0, attribute.value_ids.ids)],
                        },
                    )
                ],
            }
        )
        # Two variants are generated; give each its own internal reference.
        self.assertEqual(len(template.product_variant_ids), 2)
        order = self.env["sale.order"].create({"partner_id": self.partner.id})
        for index, variant in enumerate(template.product_variant_ids):
            size = variant.product_template_attribute_value_ids.name
            variant.default_code = "BAG-%s" % index
            # The variant display name carries the size, e.g. "[BAG-0] Baguette (Small)".
            self.assertIn(size, variant.display_name)
            line = self.env["sale.order.line"].create(
                {"order_id": order.id, "product_id": variant.id}
            )
            self.assertIn("[%s] Baguette" % variant.default_code, line.name)
            self.assertIn("Crusty loaf", line.name)
            self.assertNotIn(size, line.name)
