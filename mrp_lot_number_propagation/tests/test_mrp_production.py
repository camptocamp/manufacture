# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import random
import string

from odoo.exceptions import UserError
from odoo.tests.common import Form

from .common import Common


class TestMrpProduction(Common):

    LOT_NAME = "PROPAGATED-LOT"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Configure the BoM to propagate lot number
        cls.bom.lot_number_propagation = True
        cls.line_tracked_by_sn.propagate_lot_number = True
        with Form(cls.env["mrp.production"]) as form:
            form.bom_id = cls.bom
            cls.order = form.save()

    def _update_stock_component_qty(self, order):
        for move in order.move_raw_ids:
            if move.product_id.type != "product":
                continue
            lot = None
            if move.product_id.tracking != "none":
                lot_name = "".join(
                    random.choice(string.ascii_lowercase) for i in range(10)
                )
                if move.bom_line_id.propagate_lot_number:
                    lot_name = self.LOT_NAME
                lot = self.env["stock.production.lot"].create(
                    {
                        "product_id": move.product_id.id,
                        "company_id": move.company_id.id,
                        "name": lot_name,
                    }
                )
            self._update_qty_in_location(
                move.location_id,
                move.product_id,
                move.product_uom_qty,
                lot=lot,
            )

    def _set_qty_done(self, order):
        for line in order.move_raw_ids.move_line_ids:
            line.qty_done = line.product_uom_qty
        order.qty_producing = order.product_qty

    def test_order_propagated_lot_producing(self):
        self.assertTrue(self.order.is_lot_number_propagated)
        self._update_stock_component_qty(self.order)
        self.order.action_confirm()
        self._set_qty_done(self.order)
        self.assertEqual(self.order.propagated_lot_producing, self.LOT_NAME)

    def test_order_write_lot_producing_id_not_allowed(self):
        with self.assertRaisesRegex(UserError, "not allowed"):
            self.order.lot_producing_id = False

    def test_order_post_inventory(self):
        self._update_stock_component_qty(self.order)
        self.order.action_confirm()
        self._set_qty_done(self.order)
        self.order.button_mark_done()
        self.assertEqual(self.order.lot_producing_id.name, self.LOT_NAME)
