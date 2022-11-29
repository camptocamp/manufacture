# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _get_manufacturing_orders(self, states=None):
        self.ensure_one()
        if states is None:
            states = ("confirmed", "progress")
        return self.move_lines.move_dest_ids.raw_material_production_id.filtered(
            lambda o: o.state in states
        )

    def _action_done(self):
        res = super()._action_done()
        for picking in self:
            if picking.state != "done":
                continue
            orders = picking._get_manufacturing_orders()
            if not orders:
                continue
            for order in orders:
                # TODO add a flag on the Manufacture picking type
                order._auto_validate_after_picking()
        return res
