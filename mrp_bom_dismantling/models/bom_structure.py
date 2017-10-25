# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp.osv import osv
from openerp.addons.mrp.report.bom_structure import bom_structure


class bom_structure_dismantling(bom_structure):
    """Override to avoid mixing BOM and
    dismantling BOM in output
    """

    def __init__(self, cr, uid, name, context):
        super(bom_structure_dismantling, self).__init__(
            cr, uid, name, context=context)
        self.localcontext.update({
            'get_children': self.get_children,
        })

    def get_children(self, object, level=0):
        result = []

        def _get_rec(object, level, qty=1.0):

            for l in object:
                res = {}
                res['pname'] = l.product_id.name_get()[0][1]
                res['pcode'] = l.product_id.default_code
                res['pqty'] = l.product_qty * qty
                res['uname'] = l.product_uom.name
                res['level'] = level
                res['code'] = l.bom_id.code
                result.append(res)
                if l.bom_id.dismantling:
                    children = l.with_context(dismantling=True).child_line_ids
                else:
                    children = l.child_line_ids
                if children:
                    if level < 6:
                        level += 1
                    _get_rec(children, level, qty=res['pqty'])
                    if level > 0 and level < 6:
                        level -= 1
            return result

        children = _get_rec(object, level)
        return children


class report_mrpbomstructure(osv.AbstractModel):
    _name = 'report.mrp.report_mrpbomstructure'
    _inherit = 'report.abstract_report'
    _template = 'mrp.report_mrpbomstructure'
    _wrapped_report_class = bom_structure_dismantling
