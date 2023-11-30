# © 2016 Ucamco - Wim Audenaert <wim.audenaert@ucamco.com>
# Copyright 2016-21 ForgeFlow S.L. (https://www.forgeflow.com)
# - Jordi Ballester Alomar <jordi.ballester@forgeflow.com>
# - Lois Rilo Antelo <lois.rilo@forgeflow.com>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class MrpArea(models.Model):
    _name = "mrp.area"
    _description = "MRP Area"

    name = fields.Char(required=True)
    warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse", string="Warehouse", required=True
    )
    company_id = fields.Many2one(
        comodel_name="res.company", related="warehouse_id.company_id", store=True
    )
    location_id = fields.Many2one(
        comodel_name="stock.location", string="Location", required=True
    )
    active = fields.Boolean(default=True)
    calendar_id = fields.Many2one(
        comodel_name="resource.calendar",
        string="Working Hours",
        related="warehouse_id.calendar_id",
    )
    priorize_safety_stock = fields.Boolean(
        help="Rebuild safety stock as early as possible"
    )
    safety_stock_lead = fields.Integer(
        string="Safety stock rebuild lead time (Weeks)",
        help="Lead time for safety stock rebuilding (in weeks). "
        "This allows to consume the safety stock to satify needs and to delay "
        "rebuilding the safety stock until the production capacity is available again. "
        "Use -1 if you are not under tension and can rebuild safety stock immediately.",
        default=-1,
    )
    safety_stock_lead_week_day = fields.Selection(
        [
            ("1", "Monday"),
            ("2", "Tuesday"),
            ("3", "Wednesday"),
            ("4", "Thursday"),
            ("5", "Friday"),
            ("6", "Saturday"),
            ("7", "Sunday"),
        ],
        default="5",
        string="Safety stock lead time end day",
        help="Day of week for the end of the safety stock lead time",
    )
    safety_stock_target_date = fields.Date(
        compute="_compute_safety_stock_target_date",
        string="Safety stock lead date",
        help="We will start rebuilding safety stock on that date",
    )

    @api.model
    def _datetime_to_date_tz(self, dt_to_convert=None):
        """Coverts a datetime to date considering the timezone of MRP Area.
        If no datetime is provided, it returns today's date in the timezone."""
        return fields.Date.context_today(
            self.with_context(tz=self.calendar_id.tz),
            timestamp=dt_to_convert,
        )

    def _get_locations(self):
        self.ensure_one()
        return self.env["stock.location"].search(
            [("id", "child_of", self.location_id.id)]
        )

    @api.depends("safety_stock_lead", "safety_stock_lead_week_day")
    def _compute_safety_stock_target_date(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.safety_stock_lead < 0:
                rec.safety_stock_target_date = today
            else:
                weekday = int(rec.safety_stock_lead_week_day)
                delta = rec.safety_stock_lead * 7 + weekday - today.isoweekday()
                rec.safety_stock_target_date = today + relativedelta(days=delta)

    @api.onchange("safety_stock_lead")
    def onchange_safety_stock_lead(self):
        for rec in self:
            if rec.safety_stock_lead < 0:
                rec.safety_stock_lead_week_day = False
