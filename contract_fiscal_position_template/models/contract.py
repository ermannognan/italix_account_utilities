from odoo import api, fields, models


class ContractContract(models.Model):
    _inherit = 'contract.contract'

    @api.onchange('partner_id')
    def on_change_partner_id(self):
        res = super(ContractContract, self).on_change_partner_id()
        if self.contract_template_id:
            if self.contract_template_id.fiscal_position_id:
                self.fiscal_position_id = \
                    self.contract_template_id.fiscal_position_id
        elif self.partner_id:
            self.fiscal_position_id = self.partner_id.property_account_position_id
        return res
