# Copyright 2015 Nicola Malcontenti - Agile Business Group
# Copyright 2016 Andrea Cometa - Apulia Software
# Copyright 2016-2019 Lorenzo Battistini
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "Contract payment template",
    'summary': 'Manage payment info on contract template',
    'version': '12.0.1.0.0',
    'category': 'Account',
    'author': 'Ermanno Gnan, Hudson Ferreira da Silva',
    'website': '',
    'license': 'AGPL-3',
    'depends': [
        'contract_payment_mode',
    ],
    "data": [
        "views/contract_view.xml",
    ],
    "installable": True
}
