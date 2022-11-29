# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _auto_validate_after_picking(self):
        self.ensure_one()
        if self.state == "progress":
            # If the MO is already in progress, we want to call the immediate
            # wizard to handle lot/serial number automatically (if any).
            action = self._action_generate_immediate_wizard()
            self._handle_wiz_mrp_immediate_production(action)
        res = self.button_mark_done()
        if res is True:
            return True
        res = self.handle_mark_done_result(res)
        while isinstance(res, dict):
            res = self.handle_mark_done_result(res)

    def handle_mark_done_result(self, res):
        handler_name = "_handle_wiz_" + res["res_model"].replace(".", "_")
        handler = getattr(self, handler_name, None)
        if not handler:
            _logger.warning("'{}' wizard is not supported", res["res_model"])
            return True
        return handler(res)

    def _handle_wiz_mrp_immediate_production(self, action):
        wiz_model = self.env[action["res_model"]].with_context(
            **action.get("context", {})
        )
        wiz = wiz_model.create({})
        return wiz.process()

    def _handle_wiz_mrp_production_backorder(self, action):
        wiz_model = self.env[action["res_model"]].with_context(
            **action.get("context", {})
        )
        wiz = wiz_model.create({})
        return wiz.action_backorder()
