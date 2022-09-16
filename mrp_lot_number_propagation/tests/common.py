# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields
from odoo.tests import common


class Common(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.bom = cls.env.ref("mrp.mrp_bom_desk")
        cls.product_tracked_by_lot = cls.env.ref(
            "mrp.product_product_computer_desk_leg"
        )
        cls.product_tracked_by_sn = cls.env.ref(
            "mrp.product_product_computer_desk_head"
        )
        cls.line_tracked_by_lot = cls.bom.bom_line_ids.filtered(
            lambda o: o.product_id == cls.product_tracked_by_lot
        )
        cls.line_tracked_by_sn = cls.bom.bom_line_ids.filtered(
            lambda o: o.product_id == cls.product_tracked_by_sn
        )
        cls.line_no_tracking = fields.first(
            cls.bom.bom_line_ids.filtered(lambda o: o.product_id.tracking == "none")
        )

    @classmethod
    def _update_qty_in_location(
        cls, location, product, quantity, package=None, lot=None, in_date=None
    ):
        quants = cls.env["stock.quant"]._gather(
            product, location, lot_id=lot, package_id=package, strict=True
        )
        # this method adds the quantity to the current quantity, so remove it
        quantity -= sum(quants.mapped("quantity"))
        cls.env["stock.quant"]._update_available_quantity(
            product,
            location,
            quantity,
            package_id=package,
            lot_id=lot,
            in_date=in_date,
        )
