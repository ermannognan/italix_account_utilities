# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    use_proforma_on_invoice = fields.Boolean(
        string='Use proforma on invoices',
        related='company_id.default_use_proforma_on_invoice',
        readonly=False)
