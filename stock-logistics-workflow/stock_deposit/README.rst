[![Build Status](https://travis-ci.org/zeroincombenze/stock-logistics-workflow.svg?branch=9.0)](https://travis-ci.org/zeroincombenze/stock-logistics-workflow)
[![license agpl](https://img.shields.io/badge/licence-AGPL--3-blue.svg)](http://www.gnu.org/licenses/agpl-3.0.html)
[![Coverage Status](https://coveralls.io/repos/github/zeroincombenze/stock-logistics-workflow/badge.svg?branch=9.0)](https://coveralls.io/github/zeroincombenze/stock-logistics-workflow?branch=9.0)
[![codecov](https://codecov.io/gh/zeroincombenze/stock-logistics-workflow/branch/9.0/graph/badge.svg)](https://codecov.io/gh/zeroincombenze/stock-logistics-workflow/branch/9.0)
[![OCA_project](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-oca-9.svg)](https://github.com/OCA/stock-logistics-workflow/tree/9.0)
[![Tech Doc](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-9.svg)](http://wiki.zeroincombenze.org/en/Odoo/9.0/dev)
[![Help](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-9.svg)](http://wiki.zeroincombenze.org/en/Odoo/9.0/man/LO)
[![try it](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-9.svg)](http://erp9.zeroincombenze.it)












































































[![en](http://www.shs-av.com/wp-content/en_US.png)](http://wiki.zeroincombenze.org/it/Odoo/7.0/man)

.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

Stock deposit
=============

This module extends standard WMS to manage customers deposit locations by
warehouse.
Deposited stocks can't be selected in regular delivery orders unless you have
been returned it.
Deposited stocks have been evaluated in inventory valuation.

Installation
------------






The installation module process create a deposit location per warehouse and
two picking types, one for outgoing deposits and other for returned deposits.

Configuration
-------------






To configure this module, you need to:

#. Go to *Inventory > Settings > Product Owners* and click
   "**Manage consignee stocks (advanced)**".

Usage
-----






=====

To use this module, you need to:

#. Go to products and create one of type "Stockable".
#. Update quantities on hand to have stock of it.
#. Go to inventory dashboard and click on "Deposit out" card to do a new
   transfer.
#. Create a picking with owner and select the product to do the transfer.

To track current deposits:

#. After that process, you can view deposit quantities in product form view.
#. You can also see the deposits for all your products in the menu entry
   Inventory --> Reports --> Deposited location inventory.

For regularizing deposited quantities (this means to deliver deposited stock
to the customer as a normal outgoing move.), you need:

#. Go to Inventory --> Reports --> Deposited location inventory, select quants
   that you want to regularize and click on more actions and select
   "**Regularize deposit quants**". This process creates delivery orders from
   deposit location to customer location.

To give back deposit to you warehouse, you need:

#. Just make standard process, go to deposit picking and click in buton
   "Reverse".

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/154/9.0

Known issues / Roadmap
----------------------





Bug Tracker
-----------






Bugs are tracked on `GitHub Issues
<https://github.com/OCA/154/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
-------






Images

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/
  blob/master/template/module/static/description/icon.svg>`_.
* https://openclipart.org/detail/168751/saving-up
* https://openclipart.org/detail/171740/wooden-package







### Contributors






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
