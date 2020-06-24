# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class AccountJournal(models.Model):
    _inherit = "account.journal"

    proforma_sequence_id = fields.Many2one(
        "ir.sequence", string="Proforma entry sequence",
        help="This field contains the information related to the numbering of "
             "the credit note entries of this journal.", copy=False)
    # Da mostrare a Hudson
    proforma_sequence = fields.Boolean(
        string='Dedicated Proforma sequence',
        help="Check this box if you want to use proforma sequence for invoices "
             "from this journal", default=False)

    @api.multi
    # do not depend on 'proforma_sequence_id.date_range_ids', because
    # proforma_sequence_id._get_current_sequence() may invalidate it!
    @api.depends(
        'proforma_sequence_id.use_date_range',
        'proforma_sequence_id.number_next_actual')
    def _compute_proforma_seq_number_next(self):
        '''Compute 'sequence_number_next' according to the current sequence in use,
        an ir.sequence or an ir.sequence.date_range.
        '''
        for journal in self:
            if journal.proforma_sequence_id and journal.proforma_sequence:
                sequence = journal.proforma_sequence_id._get_current_sequence()
                journal.proforma_sequence_number_next = \
                    sequence.number_next_actual
            else:
                journal.proforma_sequence_number_next = 1

    @api.multi
    def _inverse_proforma_seq_number_next(self):
        for journal in self:
            if journal.proforma_sequence_id and journal.proforma_sequence and \
                    journal.proforma_sequence_number_next:
                sequence = journal.proforma_sequence_id._get_current_sequence()
                sequence.sudo().number_next = \
                    journal.proforma_sequence_number_next

    @api.multi
    def write(self, vals):
        result = super(AccountJournal, self).write(vals)
        for journal in self:
            company = journal.company_id

        # create the relevant refund sequence
        if vals.get('proforma_sequence'):
            for journal in self.filtered(
                    lambda j: j.type in ('sale', 'purchase') and
                    not j.proforma_sequence_id):
                journal_vals = {
                    'name': _("Proforma: ") + journal.name,
                    'company_id': journal.company_id.id,
                    'code': journal.code,
                    'proforma_sequence_number_next': vals.get(
                        'proforma_sequence_number_next',
                        journal.proforma_sequence_number_next),
                }
                journal.proforma_sequence_id = \
                    self.sudo()._create_sequence(
                        journal_vals, proforma=True).id  # modificare creando proforma...

        return result
