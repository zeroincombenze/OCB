[![Build Status](https://travis-ci.org/zeroincombenze/openerp_report_designer.svg?branch=7.0)](https://travis-ci.org/zeroincombenze/openerp_report_designer)
[![license agpl](https://img.shields.io/badge/licence-AGPL--3-blue.svg)](http://www.gnu.org/licenses/agpl-3.0.html)
[![Coverage Status](https://coveralls.io/repos/github/zeroincombenze/openerp_report_designer/badge.svg?branch=7.0)](https://coveralls.io/github/zeroincombenze/openerp_report_designer?branch=7.0)
[![codecov](https://codecov.io/gh/zeroincombenze/openerp_report_designer/branch/7.0/graph/badge.svg)](https://codecov.io/gh/zeroincombenze/openerp_report_designer/branch/7.0)
[![OCA_project](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-oca-7.svg)](https://github.com/OCA/openerp_report_designer/tree/7.0)
[![Tech Doc](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-7.svg)](http://wiki.zeroincombenze.org/en/Odoo/7.0/dev)
[![Help](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-7.svg)](http://wiki.zeroincombenze.org/en/Odoo/7.0/man/)
[![try it](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-7.svg)](http://erp7.zeroincombenze.it)


[![en](http://www.shs-av.com/wp-content/en_US.png)](http://wiki.zeroincombenze.org/it/Odoo/7.0/man)

About Odoo Report Designer Plugin
=================================
Odoo Report Desinger Plugin is a Package of OpenOffice Writer.
Using this Plugin , we can modify existing Odoo Reports and also we can make new nice OpenERP Reports.


How to Install Odoo Report Designer Plugin into Openoffice 3.2 in Linux?
- In Openoffice writer, Open Extension Manager window from Tools > Extension Menu

- Click on "Add" button and select path where the openerp_report_designer.zip is located.

- On the completion of adding package you will get your package
  under 'Extension Manager' and the status of your package become 'Enabled'

- Close openoffice writer.

- Restart openoffice writer, Now you will find one new menu "Odoo Report Designer" in Menubar.


How to install the plugin with OpenOffice 2.4 on Windows

If you get an error for the installation of the plugin, edit the pythonloader.py file
in $(OPEN_OFFICE_DIR)\program\ and change the value of DEBUG to None.

If you get an error for the uno.exe in window then just close the Quick starter
	Openoffice.2.4.1 Too\Option\Openoffic.org in that select the Memory
	in that Openoffice.org.QuickStarter
	if checked mark is there then just remove it..

If you are using OpenOffice 3.0 and install the Report Desinger with make all
	command then change  path in makefile

	sh /opt/openoffice.org3/program/unopkg add or remove both

	And for previous version of Openoffice used

	sh /usr/lib/openoffice/program/unopkg add -v $(ZIP_FILE)

[//]: # (copyright)

----

**Odoo** is a trademark of [Odoo S.A.](https://www.odoo.com/) (formerly OpenERP, formerly TinyERP)

**OCA**, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

**zeroincombenze®** is a trademark of [SHS-AV s.r.l.](http://www.shs-av.com/)
which distributes and promotes **Odoo** ready-to-use on its own cloud infrastructure.
[Zeroincombenze® distribution](http://wiki.zeroincombenze.org/en/Odoo)
is mainly designed for Italian law and markeplace.
Everytime, every Odoo DB and customized code can be deployed on local server too.

[//]: # (end copyright)

[//]: # (addons)

[//]: # (end addons)

[![chat with us](https://www.shs-av.com/wp-content/chat_with_us.gif)](https://tawk.to/85d4f6e06e68dd4e358797643fe5ee67540e408b)
