# -*- coding: utf-8 -*-
{
    'name': "Gestion des opérations",

    'summary': "GESTION DES OPERATIONS TLT",

    'author': "Fenosoa RAHARIJAONA / m0r7y",

    'version': '10.0.2.0',

    'depends': ['base', 'mail', 'account', 'custom_report'],

    'data': [
             'datas/sequence_data.xml',
             'datas/mail_template.xml',
             'security/res_groups.xml',
             'security/ir.model.access.csv',
             'wizards/wiz_select_mail.xml',
             'views/documentation_views.xml',
             'views/transit_management.xml',
             'views/transit_management_line.xml',
             'views/res_shipper.xml',
             'wizards/register_situation_payment.xml',
             'views/state_form.xml',
             'reports/fcr_report.xml',
             'reports/bad_report.xml',
             'reports/situation_report.xml',
    ],
    
    'application': True,
    'sequence': 0,
}
