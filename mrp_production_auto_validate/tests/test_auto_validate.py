# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests.common import Form, SavepointCase


class TestManufacturingOrderAutoValidate(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.bom = cls.env.ref("mrp.mrp_bom_table_top")  # Tracked by S/N
        # Configure the WH to manufacture in at least two steps to get a
        # "pick components" transfer operation
        cls.wh = cls.env.ref("stock.warehouse0")
        cls.wh.manufacture_steps = "pbm"

    @classmethod
    def _create_manufacturing_order(cls, bom, product_qty=1):
        with Form(cls.env["mrp.production"]) as form:
            form.bom_id = bom
            form.product_qty = product_qty
            order = form.save()
            order.invalidate_cache()
            return order

    @classmethod
    def _validate_picking(cls, picking, half=False):
        for move_line in picking.move_line_ids:
            qty = move_line.product_uom_qty
            move_line.qty_done = qty / 2 if half else qty
        picking._action_done()

    def test_get_manufacturing_orders_pbm(self):
        """Get the MO from transfers in a 2 steps configuration."""
        # WH already configured as 'Pick components and then manufacture (2 steps)'
        order = self._create_manufacturing_order(self.bom)
        order.action_confirm()
        picking_pick = order.picking_ids
        self.assertEqual(picking_pick._get_manufacturing_orders(), order)

    def test_get_manufacturing_orders_pbm_sam(self):
        """Get the MO from transfers in a 3 steps configuration."""
        self.wh.manufacture_steps = "pbm_sam"
        order = self._create_manufacturing_order(self.bom)
        order.action_confirm()
        picking_pick = order.picking_ids.filtered(
            lambda o: "Pick" in o.picking_type_id.name
        )
        picking_store = order.picking_ids.filtered(
            lambda o: "Store" in o.picking_type_id.name
        )
        self.assertEqual(picking_pick._get_manufacturing_orders(), order)
        self.assertFalse(picking_store._get_manufacturing_orders())

    def test_auto_validate(self):
        """Auto-validation of MO when 'pick components' transfer is validated."""
        order = self._create_manufacturing_order(self.bom)
        order.action_confirm()
        self.assertEqual(order.state, "confirmed")
        picking = order.picking_ids
        picking.action_assign()
        self.assertEqual(picking.state, "assigned")
        self._validate_picking(picking)
        self.assertEqual(picking.state, "done")
        self.assertEqual(order.state, "done")
        self.assertTrue(order.lot_producing_id)

    def test_auto_validate_with_backorder(self):
        order = self._create_manufacturing_order(self.bom, product_qty=2)
        order.action_confirm()
        self.assertEqual(order.state, "confirmed")
        # Progress 'Pick components' partially
        picking = order.picking_ids
        picking.action_assign()
        self.assertEqual(picking.state, "assigned")
        self._validate_picking(picking, half=True)  # To get a backorder
        self.assertTrue(picking.backorder_ids)
        # Check we get one MO validated and the remaining one to process
        order_done = picking._get_manufacturing_orders(states=("done",))
        self.assertTrue(order_done)
        order_wip = picking._get_manufacturing_orders()
        self.assertTrue(order_wip)
        # Process the backorder
        self._validate_picking(picking.backorder_ids.with_context(BLABLA=True))
        self.assertEqual(picking.backorder_ids.state, "done")
        self.assertEqual(order_wip.state, "done")
