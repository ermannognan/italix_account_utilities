# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from odoo.exceptions import UserError
import re

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    proforma_number = fields.Char(
        string="Proforma number", copy=False, readonly=True)
    proforma_version = fields.Integer(
        string="Proforma version", required=True, readonly=True, default=0)
    proforma_date = fields.Date(string="Proforma date", required=False)
    is_proforma = fields.Boolean(
        string="Is proforma", compute="_compute_is_proforma", store=True)
    proforma_sequence_number_next = fields.Char(
        string="Proforma next number", compute="_get_sequence_number_next",
        inverse="_set_proforma_sequence_next")
    proforma_sequence_number_next_prefix = fields.Char(
        string="Proforma next Number prefix",
        compute="_get_sequence_prefix")
    proforma_version_str = fields.Char(
        string="Proforma version",
        compute="_get_proforma_info")
    proforma_number_with_version = fields.Char(
        string="Proforma version",
        compute="_get_proforma_info")
    proforma_has_changed = fields.Boolean(
        string="Proforma has changed", default=True)

    _sql_constraints = [(
        "proforma_number_uniq",
        "unique(proforma_number, company_id, journal_id, type)",
        "Invoice proforma number must be unique per company!"),
    ]

    @api.multi
    @api.depends("proforma_version", "proforma_number")
    def _get_proforma_info(self):
        for invoice in self:
            version = "/V%03d" % invoice.proforma_version
            invoice.proforma_version_str = version
            if invoice.proforma_number:
                invoice.proforma_number_with_version = \
                    invoice.proforma_number + version
            else:
                invoice.proforma_number_with_version = False

    @api.multi
    def action_invoice_sent(self):
        self.ensure_one()
        if not self.invoice_line_ids:
            raise UserError(_("This invoice has no lines!"))
        if self.is_proforma:
            if not self.proforma_number:
                self.proforma_number = \
                    self.proforma_sequence_number_next_prefix + \
                    self.proforma_sequence_number_next
                #  sequence next()
            if self.proforma_has_changed:
                self.proforma_version += 1
                self.proforma_has_changed = False
        if self._context.get("template_proforma"):
            template = self.env.ref("account_invoice_proforma.email_template_edi_proforma_invoice", False)
            compose_form = self.env.ref("account.account_invoice_send_wizard_form", False)
            lang = self.env.context.get("lang")
            if template and template.lang:
                lang = template._render_template(template.lang, "account.invoice", self.id)
            self = self.with_context(lang=lang)
            invoice_types = {
                "out_invoice": _("Invoice"),
                "in_invoice": _("Vendor Bill"),
                "out_refund": _("Credit Note"),
                "in_refund": _("Vendor Credit note"),
            }
            ctx = dict(
                default_model="account.invoice",
                default_res_id=self.id,
                default_use_template=bool(template),
                default_template_id=template and template.id or False,
                default_composition_mode="comment",
                mark_invoice_as_sent=True,
                model_description=invoice_types[self.type],
                custom_layout="mail.mail_notification_paynow",
                force_email=True
            )
            return {
                "name": _("Send Invoice"),
                "type": "ir.actions.act_window",
                "view_type": "form",
                "view_mode": "form",
                "res_model": "account.invoice.send",
                "views": [(compose_form.id, "form")],
                "view_id": compose_form.id,
                "target": "new",
                "context": ctx,
            }
        else:
            res = super(AccountInvoice, self).action_invoice_sent()
        return res



    @api.multi
    def _set_proforma_sequence_next(self):
        self.ensure_one()
        proforma_journal_sequence, domain = \
            self._get_proforma_seq_number_next_stuff()
        if not self.env.user._is_admin() or \
                not self.proforma_sequence_number_next or \
                self.search_count(domain):
            return
        nxt = re.sub("[^0-9]", "", self.proforma_sequence_number_next)
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





