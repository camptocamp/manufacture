# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests.common import Form, SavepointCase


class TestMrpLotProductionDate(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.bom = cls.env.ref("mrp.mrp_bom_table_top")  # Tracked by S/N
        cls.bom.product_id.use_production_date = True

    @classmethod
    def _create_manufacturing_order(cls, bom, product_qty=1):
        with Form(cls.env["mrp.production"]) as form:
            form.bom_id = bom
            form.product_qty = product_qty
            order = form.save()
            order.invalidate_cache()
            return order

    def test_lot_production_date(self):
        order = self._create_manufacturing_order(self.bom)
        order.action_generate_serial()
        self.assertTrue(order.lot_producing_id.production_date)
