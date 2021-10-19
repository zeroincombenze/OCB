{
    'name': 'List View Fixed Table Header',
    'version': '1.2',
    'category': 'Tools',
    'sequence': 15,
    'summary': 'Web List View Fixed Table Header',
    'description': """
Web List View Fixed Table Header
=================================
* Fixed (sticky) list view table header, very helpful when dealing with many record.
""",
    'author': 'Deneroteam',
    'website': 'www.deneroteam.com',
    'depends': ['web','base'],
    'js' : [
        'static/src/js/web_list_view_sticky.js',
    ],
    'css' : [
        "static/src/css/base.css",
    ],
    'installable': True,
    'auto_install': False,
    'application': False,

}