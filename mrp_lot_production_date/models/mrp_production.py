# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def action_generate_serial(self):
        res = super().action_generate_serial()
        if self.lot_producing_id.product_id.use_production_date:
            self.lot_producing_id.production_date = fields.Datetime.now()
        return res
