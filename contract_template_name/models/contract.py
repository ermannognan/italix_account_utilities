from odoo import api, fields, models


class ContractContract(models.Model):
    _inherit = 'contract.contract'

    @api.onchange('partner_id')
    def on_change_partner_id(self):
        res = super(ContractContract, self).on_change_partner_id()
        if self.contract_template_id and self.partner_id:
            self.name = u"%s: %s" % (
                self.contract_template_id.name, self.partner_id.name)
        else:
            self.name = False
        return res


    @api.onchange('contract_template_id')
    def _onchange_contract_template_id(self):
        res = super(ContractContract, self)._onchange_contract_template_id()
        if self.contract_template_id and self.partner_id:
            self.name = u"%s: %s" % (
                self.contract_template_id.name, self.partner_id.name)
        else:
            self.name = False
        return res
