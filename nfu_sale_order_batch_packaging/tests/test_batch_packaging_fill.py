from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestBatchPackagingFill(TransactionCase):
    def setUp(self):
        super().setUp()
        self.uom_kg = self.env.ref("uom.product_uom_kgm")
        self.uom_unit = self.env.ref("uom.product_uom_unit")
        self.partner = self.env["res.partner"].create({"name": "Test Partner"})
        self.batch = self.env["sale.order.batch"].create(
            {"name": "Test Batch", "state": "in_progress"}
        )

    def _make_product(self, uom, packaging_qty):
        product = self.env["product.product"].create(
            {
                "name": f"Product {uom.name} {packaging_qty}",
                "uom_id": uom.id,
                "uom_po_id": uom.id,
                "type": "consu",
            }
        )
        self.env["product.packaging"].create(
            {
                "name": "Pack",
                "product_id": product.id,
                "qty": packaging_qty,
                "sales": True,
            }
        )
        return product

    def _add_lines(self, product, lines_data):
        """Create one sale order in self.batch with one line per (qty, max_qty) pair.
        Returns the sale.order.batch.product that aggregates all lines."""
        order = self.env["sale.order"].create(
            {"partner_id": self.partner.id, "batch_id": self.batch.id}
        )
        for qty, max_qty in lines_data:
            self.env["sale.order.line"].create(
                {
                    "order_id": order.id,
                    "product_id": product.id,
                    "product_uom_qty": qty,
                    "product_uom_max_qty": max_qty,
                    "price_unit": 10.0,
                }
            )
        return self.batch.product_ids.filtered(lambda p: p.product_id == product)

    # ------------------------------------------------------------------
    # _fill_packaging
    # ------------------------------------------------------------------

    def test_even_split(self):
        """All lines with identical room each receive an equal share."""
        product = self._make_product(self.uom_kg, 10.0)
        # total = 24, open = 6; each line has exactly 3 kg of room
        bp = self._add_lines(product, [(7.0, 10.0), (8.0, 11.0), (9.0, 12.0)])
        self.assertAlmostEqual(bp.open_packaging_qty, 6.0, places=2)

        bp._fill_packaging(0.001)

        self.assertAlmostEqual(bp.open_packaging_qty, 0.0, places=2)
        # each line must have gained exactly 2 kg
        for line in bp.sale_order_line_ids:
            self.assertAlmostEqual(
                line.product_uom_qty,
                line.product_uom_max_qty - 1.0,
                places=3,
            )

    def test_constrained_line_capped_at_max(self):
        """A line that cannot take its fair share is capped; remainder is spread evenly."""
        product = self._make_product(self.uom_kg, 10.0)
        # total = 23, open = 7
        # rooms: 1 (capped), 10, 7 → sorted: 1, 7, 10
        bp = self._add_lines(product, [(8.0, 9.0), (5.0, 15.0), (10.0, 17.0)])
        self.assertAlmostEqual(bp.open_packaging_qty, 7.0, places=2)

        bp._fill_packaging(0.001)

        self.assertAlmostEqual(bp.open_packaging_qty, 0.0, places=2)
        capped = bp.sale_order_line_ids.filtered(
            lambda line: line.product_uom_max_qty == 9.0
        )
        # capped line must be at its max
        self.assertAlmostEqual(capped.product_uom_qty, 9.0, places=3)
        # every line must stay within its max
        for line in bp.sale_order_line_ids:
            self.assertLessEqual(line.product_uom_qty, line.product_uom_max_qty + 1e-6)

    def test_whole_units_rounding_produces_integers(self):
        """precision=1.0 yields only whole-number additions."""
        product = self._make_product(self.uom_unit, 6.0)
        # total = 7, open = 5; rooms: 3 and 5
        bp = self._add_lines(product, [(3.0, 6.0), (4.0, 9.0)])
        self.assertAlmostEqual(bp.open_packaging_qty, 5.0, places=2)
        orig = {line.id: line.product_uom_qty for line in bp.sale_order_line_ids}

        bp._fill_packaging(1.0)

        self.assertAlmostEqual(bp.open_packaging_qty, 0.0, places=2)
        for line in bp.sale_order_line_ids:
            added = line.product_uom_qty - orig[line.id]
            self.assertAlmostEqual(added, round(added), places=6)

    def test_decimal_rounding_uses_tenth_steps(self):
        """precision=0.1 distributes in 0.1-unit steps."""
        product = self._make_product(self.uom_kg, 10.0)
        # total = 7, open = 3; rooms: 7 and 6 → sorted: line2(6), line1(7)
        bp = self._add_lines(product, [(3.0, 10.0), (4.0, 10.0)])
        self.assertAlmostEqual(bp.open_packaging_qty, 3.0, places=2)
        orig = {line.id: line.product_uom_qty for line in bp.sale_order_line_ids}

        bp._fill_packaging(0.1)

        self.assertAlmostEqual(bp.open_packaging_qty, 0.0, places=2)
        for line in bp.sale_order_line_ids:
            added = round(line.product_uom_qty - orig[line.id], 6)
            # must be a multiple of 0.1 (within floating-point tolerance)
            self.assertAlmostEqual(round(added / 0.1) * 0.1, added, places=5)

    def test_sub_rounding_remainder_is_attached(self):
        """A remainder smaller than the rounding step is added directly to the last line."""
        product = self._make_product(self.uom_kg, 3.0)
        # total = 2.7, open = 0.3; with precision=1.0 every fair_share rounds to 0
        bp = self._add_lines(product, [(0.9, 1.5), (0.9, 1.5), (0.9, 1.5)])
        self.assertAlmostEqual(bp.open_packaging_qty, 0.3, places=2)

        bp._fill_packaging(1.0)

        # The whole 0.3 remainder must have been placed on one line
        self.assertAlmostEqual(bp.open_packaging_qty, 0.0, places=2)
        # Every line must still respect its max qty
        for line in bp.sale_order_line_ids:
            self.assertLessEqual(line.product_uom_qty, line.product_uom_max_qty + 1e-6)

    def test_no_line_exceeds_max_qty(self):
        """After filling no sale order line may exceed its max qty."""
        product = self._make_product(self.uom_kg, 10.0)
        bp = self._add_lines(product, [(6.0, 8.0), (7.0, 12.0), (4.0, 9.0)])
        bp._fill_packaging(0.001)
        for line in bp.sale_order_line_ids:
            self.assertLessEqual(line.product_uom_qty, line.product_uom_max_qty + 1e-6)

    # ------------------------------------------------------------------
    # Wizard
    # ------------------------------------------------------------------

    def test_wizard_includes_eligible_products_only(self):
        """Eligible products land in line_ids; ineligible ones land in zero_line_ids."""
        eligible = self._make_product(self.uom_kg, 10.0)
        ineligible = self._make_product(self.uom_kg, 10.0)
        # eligible: total max (30) covers needed (23+7=30)
        self._add_lines(eligible, [(23.0, 30.0)])
        # ineligible: total max (24) < 23+7=30 → open_packaging_max_qty != 0
        self._add_lines(ineligible, [(23.0, 24.0)])

        action = self.batch.action_fill_packages()
        wizard = self.env["sale.order.batch.packaging.fill"].browse(action["res_id"])

        self.assertEqual(len(wizard.line_ids), 1)
        self.assertEqual(wizard.line_ids.product_id, eligible)
        self.assertEqual(len(wizard.zero_line_ids), 1)
        self.assertEqual(wizard.zero_line_ids.product_id, ineligible)

    def test_wizard_default_precision_for_unit_uom(self):
        """UOMs with batch_fill_precision=1.0 default to precision 1.0."""
        product = self._make_product(self.uom_unit, 6.0)
        self._add_lines(product, [(3.0, 9.0)])

        action = self.batch.action_fill_packages()
        wizard = self.env["sale.order.batch.packaging.fill"].browse(action["res_id"])

        self.assertAlmostEqual(wizard.line_ids.batch_fill_precision, 1.0)

    def test_wizard_default_precision_for_stueck_uom(self):
        """Stück UOM (batch_fill_precision=1.0) defaults to precision 1.0."""
        uom_stueck = self.env.ref("nfu_sale_order_batch_packaging.product_uom_stueck")
        product = self._make_product(uom_stueck, 6.0)
        self._add_lines(product, [(3.0, 9.0)])

        action = self.batch.action_fill_packages()
        wizard = self.env["sale.order.batch.packaging.fill"].browse(action["res_id"])

        self.assertAlmostEqual(wizard.line_ids.batch_fill_precision, 1.0)

    def test_wizard_default_precision_for_kg_uom(self):
        """UOMs with default batch_fill_precision use 0.1."""
        product = self._make_product(self.uom_kg, 10.0)
        self._add_lines(product, [(23.0, 30.0)])

        action = self.batch.action_fill_packages()
        wizard = self.env["sale.order.batch.packaging.fill"].browse(action["res_id"])

        self.assertAlmostEqual(wizard.line_ids.batch_fill_precision, 0.1)

    def test_wizard_fill_closes_open_packaging(self):
        """End-to-end: confirming the wizard brings open_packaging_qty to zero."""
        product = self._make_product(self.uom_kg, 10.0)
        bp = self._add_lines(product, [(23.0, 30.0)])
        self.assertGreater(bp.open_packaging_qty, 0.0)

        action = self.batch.action_fill_packages()
        wizard = self.env["sale.order.batch.packaging.fill"].browse(action["res_id"])
        wizard.action_fill()

        self.assertAlmostEqual(bp.open_packaging_qty, 0.0, places=2)

    # ------------------------------------------------------------------
    # Restore
    # ------------------------------------------------------------------

    def test_restore_batch_resets_all_lines(self):
        """action_restore_ordered_qty on the batch sets every line back to ordered qty."""
        product = self._make_product(self.uom_kg, 10.0)
        bp = self._add_lines(product, [(23.0, 30.0)])
        bp._fill_packaging(0.1)
        # fill must have increased some qty
        self.assertTrue(
            any(
                line.product_uom_qty != line.product_uom_ordered_qty
                for line in bp.sale_order_line_ids
            )
        )
        self.batch.action_restore_ordered_qty()
        for line in bp.sale_order_line_ids:
            self.assertAlmostEqual(
                line.product_uom_qty, line.product_uom_ordered_qty, places=3
            )

    def test_restore_batch_product_resets_its_lines_only(self):
        """action_restore_ordered_qty on a batch product only touches its own lines."""
        product_a = self._make_product(self.uom_kg, 10.0)
        product_b = self._make_product(self.uom_kg, 10.0)
        bp_a = self._add_lines(product_a, [(23.0, 30.0)])
        bp_b = self._add_lines(product_b, [(23.0, 30.0)])
        bp_a._fill_packaging(0.1)
        bp_b._fill_packaging(0.1)

        bp_a.action_restore_ordered_qty()

        for line in bp_a.sale_order_line_ids:
            self.assertAlmostEqual(
                line.product_uom_qty, line.product_uom_ordered_qty, places=3
            )
        # product_b lines must be unchanged
        self.assertTrue(
            any(
                line.product_uom_qty != line.product_uom_ordered_qty
                for line in bp_b.sale_order_line_ids
            )
        )

    def test_has_qty_adjusted_false_before_fill(self):
        """has_qty_adjusted is False when no line has been modified."""
        product = self._make_product(self.uom_kg, 10.0)
        self._add_lines(product, [(10.0, 15.0)])
        self.assertFalse(self.batch.has_qty_adjusted)

    def test_has_qty_adjusted_true_after_fill(self):
        """has_qty_adjusted becomes True once a line quantity is increased."""
        product = self._make_product(self.uom_kg, 10.0)
        bp = self._add_lines(product, [(23.0, 30.0)])
        bp._fill_packaging(0.1)
        self.assertTrue(self.batch.has_qty_adjusted)

    def test_has_qty_adjusted_false_after_restore(self):
        """has_qty_adjusted returns to False after restoring ordered quantities."""
        product = self._make_product(self.uom_kg, 10.0)
        bp = self._add_lines(product, [(23.0, 30.0)])
        bp._fill_packaging(0.1)
        self.batch.action_restore_ordered_qty()
        self.assertFalse(self.batch.has_qty_adjusted)

    def test_has_fillable_packages_false_when_no_open_qty(self):
        """has_fillable_packages is False when all products have complete packages."""
        product = self._make_product(self.uom_kg, 10.0)
        self._add_lines(product, [(10.0, 15.0)])  # qty is exact multiple of packaging
        self.assertFalse(self.batch.has_fillable_packages)

    def test_has_fillable_packages_true_for_eligible(self):
        """has_fillable_packages is True when an eligible product has open packaging qty."""
        product = self._make_product(self.uom_kg, 10.0)
        self._add_lines(product, [(23.0, 30.0)])  # open_packaging_max_qty == 0
        self.assertTrue(self.batch.has_fillable_packages)

    def test_has_fillable_packages_true_for_ineligible(self):
        """has_fillable_packages is True even for ineligible (zero-out) products."""
        product = self._make_product(self.uom_kg, 10.0)
        self._add_lines(
            product, [(23.0, 24.0)]
        )  # max too tight → open_packaging_max_qty != 0
        self.assertGreater(
            self.batch.product_ids.filtered(
                lambda p: p.product_id == product
            ).open_packaging_max_qty,
            0.0,
        )
        self.assertTrue(self.batch.has_fillable_packages)

    # ------------------------------------------------------------------
    # Zero-out
    # ------------------------------------------------------------------

    def test_zero_packaging_sets_lines_to_zero(self):
        """_zero_packaging sets all sale order line quantities to 0."""
        product = self._make_product(self.uom_kg, 10.0)
        bp = self._add_lines(product, [(23.0, 24.0)])  # ineligible (max too tight)
        self.assertGreater(bp.open_packaging_qty, 0.0)

        bp._zero_packaging()

        for line in bp.sale_order_line_ids:
            self.assertAlmostEqual(line.product_uom_qty, 0.0, places=3)

    def test_wizard_zeros_ineligible_by_default(self):
        """Confirming the wizard zeros ineligible lines (keep_qty=False default)."""
        ineligible = self._make_product(self.uom_kg, 10.0)
        self._add_lines(ineligible, [(23.0, 24.0)])
        bp = self.batch.product_ids.filtered(lambda p: p.product_id == ineligible)

        action = self.batch.action_fill_packages()
        wizard = self.env["sale.order.batch.packaging.fill"].browse(action["res_id"])
        self.assertFalse(wizard.zero_line_ids.keep_qty)

        wizard.action_fill()

        for line in bp.sale_order_line_ids:
            self.assertAlmostEqual(line.product_uom_qty, 0.0, places=3)

    def test_wizard_keeps_ineligible_when_keep_qty_true(self):
        """Lines with keep_qty=True are not zeroed out."""
        ineligible = self._make_product(self.uom_kg, 10.0)
        bp = self._add_lines(ineligible, [(23.0, 24.0)])
        orig_qtys = {line.id: line.product_uom_qty for line in bp.sale_order_line_ids}

        action = self.batch.action_fill_packages()
        wizard = self.env["sale.order.batch.packaging.fill"].browse(action["res_id"])
        wizard.zero_line_ids.write({"keep_qty": True})
        wizard.action_fill()

        for line in bp.sale_order_line_ids:
            self.assertAlmostEqual(line.product_uom_qty, orig_qtys[line.id], places=3)

    def test_wizard_respects_precision_override(self):
        """Overriding batch_fill_precision on a wizard line changes the applied rounding."""
        product = self._make_product(self.uom_kg, 10.0)
        # total = 7, open = 3; use 2 lines (rooms: 7 and 6)
        bp = self._add_lines(product, [(3.0, 10.0), (4.0, 10.0)])

        action = self.batch.action_fill_packages()
        wizard = self.env["sale.order.batch.packaging.fill"].browse(action["res_id"])
        # Force whole-units even though UOM is kg
        wizard.line_ids.write({"batch_fill_precision": 1.0})
        wizard.action_fill()

        self.assertAlmostEqual(bp.open_packaging_qty, 0.0, places=2)
        for line in bp.sale_order_line_ids:
            # additions must be whole numbers when precision=1.0
            self.assertAlmostEqual(
                line.product_uom_qty, round(line.product_uom_qty), places=6
            )
