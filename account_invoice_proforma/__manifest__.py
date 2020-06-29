# Copyright 2015 Nicola Malcontenti - Agile Business Group
# Copyright 2016 Andrea Cometa - Apulia Software
# Copyright 2016-2019 Lorenzo Battistini
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "Account Invoice Proforma",
    'summary': 'Adds proforma state',
    'version': '12.0.1.0.0',
    'category': 'Account',
    'author': 'Ermanno Gnan, Hudson Ferreira da Silva',
    'website': '',
    'license': 'AGPL-3',
    'depends': [
        'account',
    ],
    "data": [
        'data/data.xml',
        'report/account_invoice_report.xml',
        'views/account_invoice_view.xml',
        'views/res_partner_view.xml',
        'views/res_config_settings_views.xml',
        'views/account_journal_view.xml',
    ],
    "installable": True
}
