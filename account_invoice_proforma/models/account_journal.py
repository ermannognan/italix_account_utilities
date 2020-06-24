# Copyright (C) 2018 - TODAY, Pavlov Media
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _


class AccountJournal(models.Model):
    _inherit = "account.journal"

    proforma_sequence_id = fields.Many2one(
        "ir.sequence", string="Proforma entry sequence",
        help="This field contains the information related to the numbering of "
             "the credit note entries of this journal.", copy=False)
    proforma_sequence = fields.Boolean(
        string='Dedicated Proforma sequence',
        help="Check this box if you want to use proforma sequence for invoices "
             "from this journal", default=False)
    proforma_sequence_number_next = fields.Integer(
        string='Proforma: Next Number',
        help='The next sequence number will be used for the next proforma invoice.',
        compute='_compute_proforma_seq_number_next',
        inverse='_inverse_proforma_seq_number_next')

    @api.multi
    # do not depend on 'proforma_sequence_id.date_range_ids', because
    # proforma_sequence_id._get_current_sequence() may invalidate it!
    @api.depends('proforma_sequence_id.use_date_range', 'proforma_sequence_id.number_next_actual')
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
        '''Inverse 'proforma_sequence_number_next' to edit the current sequence next number.
        '''
        for journal in self:
            if journal.proforma_sequence_id and journal.proforma_sequence and \
                    journal.proforma_sequence_number_next:
                sequence = journal.proforma_sequence_id._get_current_sequence()
                sequence.sudo().number_next = \
                    journal.proforma_sequence_number_next

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
                    self.sudo().with_context(
                        proforma_sequence=True)._create_sequence(
                        journal_vals, refund=False).id
        return result

    @api.model
    def _get_sequence_prefix(self, code, refund=False):
        is_proforma = self._context.get('proforma_sequence')
        if is_proforma:
            prefix = code.upper()
            prefix = 'P' + prefix
            return prefix + '/%(range_year)s/'
        else:
            return super(
                AccountJournal, self)._get_sequence_prefix(code, refund)



    @api.model
    def _create_sequence(self, vals, refund=False):
        is_proforma = self._context.get('proforma_sequence')
        if is_proforma:
            """ Create new no_gap entry sequence for every new Journal"""
            prefix = self._get_sequence_prefix(vals['code'], False)
            seq_name = vals['code'] + _(': Proforma') or vals['code']
            seq = {
                'name': _('%s Sequence') % seq_name,
                'implementation': 'no_gap',
                'prefix': prefix,
                'padding': 4,
                'number_increment': 1,
                'use_date_range': True,
            }
            if 'company_id' in vals:
                seq['company_id'] = vals['company_id']
            seq = self.env['ir.sequence'].create(seq)
            seq_date_range = seq._get_current_sequence()
            seq_date_range.number_next = \
                vals.get('proforma_sequence_number_next', 1) or vals.get(
                    'sequence_number_next', 1)
            return seq
        else:
            return super(
                AccountJournal, self)._create_sequence(vals, refund)
