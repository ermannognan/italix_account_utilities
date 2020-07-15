from odoo import api, models, fields


class ContractAbstractContract(models.AbstractModel):
    _inherit = 'contract.abstract.contract'

    fiscal_position_id = fields.Many2one(
        comodel_name='account.fiscal.position',
        string='Fiscal Position',
        ondelete='restrict',
    )
