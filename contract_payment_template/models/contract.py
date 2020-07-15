from odoo import api, fields, models


class ContractContract(models.Model):
    _inherit = 'contract.contract'

    @api.onchange('partner_id')
    def on_change_partner_id(self):
        res = super(ContractContract, self).on_change_partner_id()
        if self.contract_template_id:
            if self.contract_template_id.payment_mode_id:
                self.payment_mode_id = self.contract_template_id.payment_mode_id
            if self.contract_template_id.payment_term_id:
                self.payment_term_id = self.contract_template_id.payment_term_id
        return res
