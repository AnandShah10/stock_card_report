# -*- coding: utf-8 -*-
{
    'name': 'stock_card_report',
    'version': '1.0',
    'summary': "Stock report module",
    'sequence': 10,
    'author': "anand",
    'description': """
Get stock report for any warehouse or location by date range.
""",
    'category': 'Custom/Inventory',
    'website': 'https://www.odoo.com/app/invoicing',
    'depends': ['stock', 'base', 'product','report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/stock_card_wizard.xml',
        'report/report.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'GPL-3',
}
