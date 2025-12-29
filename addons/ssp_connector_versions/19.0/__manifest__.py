# -*- coding: utf-8 -*-
{
    'name': 'Smart Solutions Platform Connector',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Accounting',
    'summary': 'AI-powered invoice processing and automation',
    'description': """
Smart Solutions Platform Integration
=====================================

Automate invoice processing with AI-powered data extraction.

Features:
---------
* Automatic data extraction from invoices
* OCR with Google Vision API
* Integration with your existing workflow
* Real-time processing and validation
* Multi-language support (PT/EN)

This module connects your Odoo instance with Smart Solutions Platform
for automated invoice processing and data extraction.
    """,
    'author': 'Smart Solutions Platform',
    'website': 'https://24e1dc7cb2a8.ngrok-free.app',
    'license': 'LGPL-3',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/ssp_dashboard_views.xml',  # Must load first (defines action_ssp_dashboard_server)
        'views/ssp_config_views.xml',
        'views/ssp_iframe_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ssp_connector/static/src/js/ssp_dashboard.js',
            'ssp_connector/static/src/xml/ssp_dashboard.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
