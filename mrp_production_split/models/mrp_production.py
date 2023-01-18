# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def action_split(self):
        self.ensure_one()
        self._check_company()
        if self.state in ("draft", "done", "to_close", "cancel"):
            raise UserError(
                _("Cannot split a manufacturing order that is done or cancelled.")
            )
        action = self.env["ir.actions.actions"]._for_xml_id(
            "mrp_production_split.action_mrp_production_split_wizard"
        )
        action["context"] = {"default_production_id": self.id}
        return action
