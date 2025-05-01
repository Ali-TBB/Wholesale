# -*- coding: utf-8 -*-
{
    'name': 'Wholesale',
    'description': """
        This module about Wholesale add field to product.
    """,
    'sequence': 10,
    'version': '1.0',
    'category': 'Productivity',
    'depends': ['sale'],
    'data': [
        # 'security/hospital_security.xml',
        'security/ir.model.access.csv',
        'views/product.xml',
        'views/sale_type_view.xml',
        'views/sale_type_wizard_views.xml',
        'data/default_sale_types.xml'
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
