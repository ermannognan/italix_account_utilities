from odoo import api, models, fields


class ContractAbstractContract(models.AbstractModel):
    _inherit = 'contract.abstract.contract'

    payment_term_id = fields.Many2one(
        comodel_name='account.payment.term', string='Payment Terms', index=True
    )
    payment_mode_id = fields.Many2one(
        comodel_name='account.payment.mode',
        string='Payment Mode',
        domain=[('payment_type', '=', 'inbound')],
        index=True,
    )
