# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestInventoryTurnover(TransactionCase):
    def test_inventory_turnover_demo_product(self):
        """Receipts of 100 (9 months ago) and 50 (2 months ago) and a delivery
        of 30 (4 months ago) give 30 units consumed in both periods."""
        product = self.env.ref("stock_inventory_turnover_report.demo_turnover_product")
        self.assertEqual(product.qty_available, 120)
        self.assertEqual(product.qty_available_6m, 100)
        self.assertEqual(product.qty_available_12m, 0)
        self.assertEqual(product.qty_gotten_6m, 50)
        self.assertEqual(product.qty_gotten_12m, 150)
        self.assertEqual(product.qty_consumed_6m, 30)
        self.assertEqual(product.qty_consumed_12m, 30)
        self.assertAlmostEqual(product.months_of_inventory_6m, 24)
        self.assertAlmostEqual(product.inventory_turns_6m, 0.5)
        self.assertAlmostEqual(product.months_of_inventory_12m, 48)
        self.assertAlmostEqual(product.inventory_turns_12m, 0.25)
