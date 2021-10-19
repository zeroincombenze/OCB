[![Build Status](https://travis-ci.org/zeroincombenze/stock-logistics-workflow.svg?branch=9.0)](https://travis-ci.org/zeroincombenze/stock-logistics-workflow)
[![license agpl](https://img.shields.io/badge/licence-AGPL--3-blue.svg)](http://www.gnu.org/licenses/agpl-3.0.html)
[![Coverage Status](https://coveralls.io/repos/github/zeroincombenze/stock-logistics-workflow/badge.svg?branch=9.0)](https://coveralls.io/github/zeroincombenze/stock-logistics-workflow?branch=9.0)
[![codecov](https://codecov.io/gh/zeroincombenze/stock-logistics-workflow/branch/9.0/graph/badge.svg)](https://codecov.io/gh/zeroincombenze/stock-logistics-workflow/branch/9.0)
[![OCA_project](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-oca-9.svg)](https://github.com/OCA/stock-logistics-workflow/tree/9.0)
[![Tech Doc](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-9.svg)](http://wiki.zeroincombenze.org/en/Odoo/9.0/dev)
[![Help](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-9.svg)](http://wiki.zeroincombenze.org/en/Odoo/9.0/man/LO)
[![try it](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-9.svg)](http://erp9.zeroincombenze.it)












































































[![en](http://www.shs-av.com/wp-content/en_US.png)](http://wiki.zeroincombenze.org/it/Odoo/7.0/man)

   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

Auto-assignment of lots on pickings
===================================

When working with lots, it's very uncomfortable to introduce the quantity,
lot by lot, when transferring pickings from your warehouse (outgoing or
internal).

This module automatically assigns the reserved quantity as the done one, so
that you only have to change it in case of divergence, but having the
possibility of transferring directly.

Also this module adds a button in backorder confirmation wizard to auto
complete to do quantities for products without lots.

Installation
------------





Configuration
-------------






#. Make sure you have selected the proper removal strategy on your product
   categories.
#. Configure the product on the page "Inventory", field "Tracking" with one of
   these values: "By Unique Serial Number" or "By Lots".

Usage
-----






=====

#. Create an outgoing or an internal picking.
#. Include one product with lots and with enough stock.
#. Click on "Mark as Todo" button, and then on "Reserve".
#. Clicking on the icon with the three items bullet list on the "Operations"
   tab you will see that the quantities have been auto-assigned on the "Done"
   column.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/154/9.0

Known issues / Roadmap
----------------------





Bug Tracker
-----------





Credits
-------











### Contributors






* Pedro M. Baeza <pedro.baeza@tecnativa.com>
* Sergio Teruel <sergio.teruel@tecnativa.com>

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
which distributes and promotes **Odoo** ready-to-use on own cloud infrastructure.
[Zeroincombenze® distribution of Odoo](http://wiki.zeroincombenze.org/en/Odoo)
is mainly designed for Italian law and markeplace.
Users can download from [Zeroincombenze® distribution](https://github.com/zeroincombenze/OCB) and deploy on local server.

[//]: # (end copyright)

[//]: # (addons)

[//]: # (end addons)



[![chat with us](https://www.shs-av.com/wp-content/chat_with_us.gif)](https://tawk.to/85d4f6e06e68dd4e358797643fe5ee67540e408b)
