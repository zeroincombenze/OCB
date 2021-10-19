[![Build Status](https://travis-ci.org/zeroincombenze/account-closing.svg?branch=9.0)](https://travis-ci.org/zeroincombenze/account-closing)
[![license agpl](https://img.shields.io/badge/licence-AGPL--3-blue.svg)](http://www.gnu.org/licenses/agpl-3.0.html)
[![Coverage Status](https://coveralls.io/repos/github/zeroincombenze/account-closing/badge.svg?branch=9.0)](https://coveralls.io/github/zeroincombenze/account-closing?branch=9.0)
[![codecov](https://codecov.io/gh/zeroincombenze/account-closing/branch/9.0/graph/badge.svg)](https://codecov.io/gh/zeroincombenze/account-closing/branch/9.0)
[![OCA_project](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-oca-9.svg)](https://github.com/OCA/account-closing/tree/9.0)
[![Tech Doc](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-9.svg)](http://wiki.zeroincombenze.org/en/Odoo/9.0/dev)
[![Help](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-9.svg)](http://wiki.zeroincombenze.org/en/Odoo/9.0/man/FI)
[![try it](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-9.svg)](http://erp9.zeroincombenze.it)










































[![en](http://www.shs-av.com/wp-content/en_US.png)](http://wiki.zeroincombenze.org/it/Odoo/7.0/man)

   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

Invoice Start/End Dates
=======================

This module adds the fields *Start Date* and *End Date* on invoice lines. When you validate the invoice, the information is copied from invoice lines to account move lines (if you enabled the grouping option on the related journal, Odoo will not group invoice lines that have different start/end dates).

It also adds an option *Must Have Start and End Dates* on the product form (in the *Accounting* tab) ; if you enable this option, you will get an error message if you try to validate an invoice that constains such a product on one of its lines and doesn't have start/end dates on that line.

If you use this module, you may also be interested in 2 other modules:

* the module *sale_start_end_dates* from the sale-workflow OCA project: this module adds the fields *Start Date* and *End Date* on sale order lines and copies the information from sale order lines to invoice lines.

* the module *account_cutoff_prepaid* (same repository): this module allows easy computation of prepaid expenses and prepaid revenues.

Installation
------------





Configuration
-------------





Usage
-----






=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/89/9.0


Known issues / Roadmap
----------------------






* Add the start/end date field on the Qweb invoice report.

Bug Tracker
-----------






Bugs are tracked on `GitHub Issues
<https://github.com/OCA/account-closing/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
-------











### Contributors






* Alexis de Lattre <alexis.delattre@akretion.com>

### Funders

### Maintainer










.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.

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
