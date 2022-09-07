# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    is_lot_number_propagated = fields.Boolean(
        related="bom_id.lot_number_propagation",
        readonly=True,
        help=(
            "Lot/serial number is propagated "
            "from a component to the finished product."
        ),
    )
    propagated_lot_producing = fields.Char(
        compute="_compute_propagated_lot_producing",
        help=(
            "The BoM used on this manufacturing order is set to propagate "
            "lot number from one of its components. The value will be "
            "computed once the corresponding component is selected."
        ),
    )

    @api.depends(
        "move_raw_ids.bom_line_id.propagate_lot_number",
        "move_raw_ids.move_line_ids.qty_done",
        "move_raw_ids.move_line_ids.lot_id",
    )
    def _compute_propagated_lot_producing(self):
        for order in self:
            order.propagated_lot_producing = False
            move_with_lot = order.move_raw_ids.filtered(
                lambda o: o.bom_line_id.propagate_lot_number
            )
            move_lines = move_with_lot.move_line_ids
            if len(move_lines) == 1:
                line = move_lines
                if line.qty_done == 1 and line.lot_id:
                    order.propagated_lot_producing = line.lot_id.name

    def _post_inventory(self, cancel_backorder=False):
        self._create_and_assign_propagated_lot_number()
        return super()._post_inventory(cancel_backorder=cancel_backorder)

    def _create_and_assign_propagated_lot_number(self):
        for order in self:
            if not order.is_lot_number_propagated or order.lot_producing_id:
                continue
            finish_moves = order.move_finished_ids.filtered(
                lambda m: m.product_id == order.product_id
                and m.state not in ("done", "cancel")
            )
            if finish_moves and not finish_moves.quantity_done:
                order.with_context(lot_propagation=True).lot_producing_id = self.env[
                    "stock.production.lot"
                ].create(
                    {
                        "product_id": order.product_id.id,
                        "company_id": order.company_id.id,
                        "name": order.propagated_lot_producing,
                    }
                )

    def write(self, vals):
        for order in self:
            if (
                order.is_lot_number_propagated
                and "lot_producing_id" in vals
                and not self.env.context.get("lot_propagation")
            ):
                raise UserError(
                    _(
                        "Lot/Serial number is propagated from a component, "
                        "you are not allowed to change it."
                    )
                )
        return super().write(vals)
