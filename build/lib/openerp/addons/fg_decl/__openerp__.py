# -*- encoding: utf-8 -*-



{
    "name": "富光产品网络销售信息申报表",
    "author": "OpenERP",
    'complexity': "easy",
    "version": "0.2",
    "depends": ["base"],
    "category" : "富光",
    'description': '''
      富光基本模块''',
    "init_xml": [],
    "update_xml": ['security/group.xml',
        'security/ir.model.access.csv',
        'decl_view.xml'
    ],
    "demo_xml": [],
    "test": [],
    "installable":True,
    "certificate" : "",
    "active": True,
    "application":True,
}
