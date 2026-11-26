# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import ValidationError
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

    def test_inventory_turnover_custom_date_range(self):
        """Same demo moves seen through the wizard: from 6 months ago to today
        the stock goes from 100 to 120 with 50 gotten and 30 consumed."""
        product = self.env.ref("stock_inventory_turnover_report.demo_turnover_product")
        today = fields.Date.today()
        wizard = self.env["stock.inventory.turnover.custom.date"].create(
            {"date_from": today - relativedelta(months=6), "date_to": today}
        )
        action = wizard.action_open_report()
        product = product.with_context(**action["context"])
        self.assertEqual(product.qty_available_start, 100)
        self.assertEqual(product.qty_available_end, 120)
        self.assertEqual(product.qty_gotten_custom_date, 50)
        self.assertEqual(product.qty_consumed_custom_date, 30)
        self.assertAlmostEqual(
            product.inventory_turns_custom_date,
            12 / product.months_of_inventory_custom_date,
        )
        found = (
            self.env["product.product"]
            .with_context(**action["context"])
            .search([("qty_available_end", ">", 0), ("id", "=", product.id)])
        )
        self.assertEqual(found, product)

    def test_custom_date_wizard_invalid_range(self):
        wizard = self.env["stock.inventory.turnover.custom.date"].create(
            {"date_from": "2026-02-10", "date_to": "2026-02-01"}
        )
        with self.assertRaises(ValidationError):
            wizard.action_open_report()

    def test_wizards_open_for_regular_user(self):
        user = self.env["res.users"].create(
            {
                "name": "Wizard user",
                "login": "wizard_user_access",
                "groups_id": [(6, 0, [self.env.ref("stock.group_stock_user").id])],
            }
        )
        for model in ("stock.inventory.turnover.custom.date",):
            self.env[model].with_user(user).check_access("create")
