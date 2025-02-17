# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Project Template',
    'version': '18.0.0.0',
    'category': "Project",
    'license':'OPL-1',
    'summary': 'This apps helps to make project as template and make new project from the Template',
    'description': """Project Template , Make project as template and make new project from the Template, """,
    'author': 'BROWSEINFO',
    'website': 'https://www.browseinfo.com/demo-request?app=bi_project_template&version=18&edition=Community',
    'depends': ['base','project'],
    'data': [
               'security/ir.model.access.csv',
               'views/project_template_view.xml',
               'views/template_task_view.xml',
               'data/project_data.xml',
            ],
    'demo': [],
    'test': [],
    'installable':True,
    'auto_install':False,
    'application':True,
    'live_test_url':'https://www.browseinfo.com/demo-request?app=bi_project_template&version=18&edition=Community',
    "images":['static/description/Banner.gif'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
