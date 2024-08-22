# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_orig_created_production_ids(self):
        self.ensure_one()
        if self.created_production_id:
            return self.created_production_id
        mrp_production_ids = set()
        # There's a scenario where the current move is in self.move_orig_ids.move_orig_ids,
        # which would cause an infinite loop. To avoid this, we rely on a context key
        # when calling this method a few lines below.
        excluded_recursive_move = self.env.context.get("recursive_move_to_exclude")
        move_orig_ids = (
            self.move_orig_ids - excluded_recursive_move
            if excluded_recursive_move
            else self.move_orig_ids
        )
        for move in move_orig_ids:
            orig_created_production_ids = []
            recursive_move_to_exclude = None
            if self in move.move_orig_ids:
                recursive_move_to_exclude = self
            # Passing the current move in the context to exlude it and avoid the infinite loop.
            orig_created_production_ids = (
                move.with_context(recursive_move_to_exclude=recursive_move_to_exclude)
                ._get_orig_created_production_ids()
                .ids
            )
            mrp_production_ids.update(orig_created_production_ids)
        return self.env["mrp.production"].browse(mrp_production_ids)
