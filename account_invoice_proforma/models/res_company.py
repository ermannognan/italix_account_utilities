# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class Company(models.Model):
    _inherit = "res.company"

    default_use_proforma_on_invoice = fields.Boolean(
        string="Use proforma on invoices as default")
