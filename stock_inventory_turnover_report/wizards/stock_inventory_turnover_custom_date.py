# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime, time

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class StockInventoryTurnoverCustomDate(models.TransientModel):
    _name = "stock.inventory.turnover.custom.date"
    _description = "Inventory Turnover for a Custom Date Range"

    date_from = fields.Date(
        string="From",
        required=True,
        default=lambda self: fields.Date.today().replace(month=1, day=1),
    )
    date_to = fields.Date(
        string="To",
        required=True,
        default=fields.Date.today,
    )

    def action_open_report(self):
        self.ensure_one()
        if self.date_from > self.date_to:
            raise ValidationError(_("The start date must not be after the end date."))
        tree_view = self.env.ref(
            "stock_inventory_turnover_report.view_stock_inv_turns_custom_tree"
        )
        return {
            "type": "ir.actions.act_window",
            "name": _(
                "Inventory Turnover (%(date_from)s - %(date_to)s)",
                date_from=self.date_from,
                date_to=self.date_to,
            ),
            "res_model": "product.product",
            "views": [
                (tree_view.id, "list"),
                (False, "form"),
                (False, "pivot"),
                (False, "graph"),
            ],
            "domain": [("is_storable", "=", True)],
            "context": {
                "search_default_group_by_categ": True,
                "search_default_filter_is_in_stock_custom": True,
                "turnover_date_from": datetime.combine(self.date_from, time.min),
                "turnover_date_to": datetime.combine(self.date_to, time.max),
            },
        }
