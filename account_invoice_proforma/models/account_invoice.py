# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api
import re

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    proforma_number = fields.Char(
        string="Proforma number", copy=False, readonly=True)
    proforma_version = fields.Integer(
        string="Proforma version", required=True, readonly=True, default=1)
    proforma_date = fields.Date(string="Proforma date", required=False)
    is_proforma = fields.Boolean(
        string="Is proforma", compute="_compute_is_proforma", store=True)
    proforma_sequence_number_next = fields.Char(
        string="Proforma next number", compute="_get_sequence_number_next",
        inverse="_set_proforma_sequence_next")
    proforma_sequence_number_next_prefix = fields.Char(
        string="Proforma next Number prefix", 
        compute="_get_sequence_prefix")

    _sql_constraints = [(
        "proforma_number_uniq",
        "unique(proforma_number, company_id, journal_id, type)",
        "Invoice proforma number must be unique per company!"),
    ]

    @api.multi
    def _set_proforma_sequence_next(self):
        self.ensure_one()
        proforma_journal_sequence, domain = \
            self._get_proforma_seq_number_next_stuff()
        if not self.env.user._is_admin() or \
                not self.proforma_sequence_number_next or \
                self.search_count(domain):
            return
        nxt = re.sub("[^0-9]", '', self.proforma_sequence_number_next)
        result = re.match("(0*)([0-9]+)", nxt)
        if result and proforma_journal_sequence:
            # use _get_current_sequence to manage the date range sequences
            sequence_date = self.date or self.date_invoice
            sequence = \
                proforma_journal_sequence._get_current_sequence(
                    sequence_date=sequence_date)
            sequence.number_next = int(result.group(2))

    @api.depends("state", "journal_id", "journal_id.proforma_sequence_id")
    def _get_sequence_number_next(self):
        super(AccountInvoice, self)._get_sequence_number_next()
        for invoice in self:
            proforma_journal_sequence, domain = \
                invoice._get_proforma_seq_number_next_stuff()
            if invoice.is_proforma and \
                    (invoice.state == "draft") and \
                    not self.search(domain, limit=1):
                sequence_date = invoice.date or invoice.date_invoice
                number_next = \
                    proforma_journal_sequence._get_current_sequence(
                        sequence_date=sequence_date).number_next_actual
                invoice.proforma_sequence_number_next = \
                    "%%0%sd" % proforma_journal_sequence.padding % number_next
            else:
                invoice.proforma_sequence_number_next = ""
    
    def _get_proforma_seq_number_next_stuff(self):
        self.ensure_one()
        journal_sequence = self.journal_id.proforma_sequence_id
        if self.journal_id.refund_sequence:
            domain = [("type", "=", self.type)]
        elif self.type in ["in_invoice", "in_refund"]:
            domain = [("type", "in", ["in_invoice", "in_refund"])]
        else:
            domain = [("type", "in", ["out_invoice", "out_refund"])]
        if self.id:
            domain += [("id", "<>", self.id)]
        domain += [
            ("journal_id", "=", self.journal_id.id),
            ("state", "not in", ["draft", "cancel"]),
            "|",
            ("proforma_number", "!=", ""),
            ("proforma_number", "!=", False),
        ]
        return journal_sequence, domain

    @api.depends("state", "journal_id", "date", "date_invoice", "is_proforma")
    def _get_sequence_prefix(self):
        super(AccountInvoice, self)._get_sequence_prefix()
        if not self.env.user._is_system():
            for invoice in self:
                invoice.proforma_sequence_number_next_prefix = False
                invoice.proforma_sequence_number_next = ""
            return
        for invoice in self:
            proforma_journal_sequence, domain = \
                invoice._get_proforma_seq_number_next_stuff()
            sequence_date = invoice.date or invoice.date_invoice
            if invoice.is_proforma and (invoice.state == "draft") \
                    and not self.search(domain, limit=1):
                prefix, dummy = proforma_journal_sequence.with_context(
                    ir_sequence_date=sequence_date,
                    ir_sequence_date_range=sequence_date)._get_prefix_suffix()
                invoice.proforma_sequence_number_next_prefix = prefix
            else:
                invoice.proforma_sequence_number_next_prefix = False

    @api.depends(
        "state", "proforma_number", "partner_id.use_proforma_on_invoice",
        "company_id.default_use_proforma_on_invoice", "type")
    @api.multi
    def _compute_is_proforma(self):  # self is the recordset in memory to be evaluated and updated
        for invoice in self:
            invoice.is_proforma = \
                invoice.state == "draft" and \
                invoice.type in ("out_invoice", "out_refund") and \
                (invoice.proforma_number or
                    (invoice.partner_id.use_proforma_on_invoice != "no" and
                     invoice.company_id.default_use_proforma_on_invoice) or
                 invoice.partner_id.use_proforma_on_invoice == "yes")





