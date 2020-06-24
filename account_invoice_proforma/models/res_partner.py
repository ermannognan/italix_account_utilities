# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class Partner(models.Model):
    _inherit = "res.partner"

    use_proforma_on_invoice = fields.Selection(
        string="Use proforma on invoices",
        selection=[('yes', 'Yes'), ('no', 'No'), ],
        required=False)
