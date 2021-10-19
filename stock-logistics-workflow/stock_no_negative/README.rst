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

Stock Disallow Negative
=======================

By default, Odoo allows negative stock. The advantage of negative stock is that, if some stock levels are wrong in the ERP, you will not be blocked when validating the picking for a customer... so you will still be able to ship the products on time (it's an example !). The problem is that, after you forced the stock level to negative, you are supposed to fix the stock level later via an inventory ; but this action is often forgotten by users, so you end up with negative stock levels in your ERP and it can stay like this forever (or at least until the next full inventory).

If you disallow negative stock in Odoo with this module, you will be blocked when trying to validate a stock operation that will set the stock level of a product as negative. So you will have to fix the wrong stock level of that product without delay, in order to validate the stock operation in Odoo... you can't forget it anymore !

Installation
------------





Configuration
-------------






By default, the stockable products will not be allowed to have a negative stock. If you want to make some exceptions for some products or some product categories, you can activate the option *Allow Negative Stock* on some products or some products categories.

Usage
-----






=====

When you validate a stock operation (a stock move, a picking, a manufacturing order, etc.) that will set the stock level of a stockable product as negative, you will be blocked by an error message. The consumable products can still have a negative stock level.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/154/9.0

Known issues / Roadmap
----------------------





Bug Tracker
-----------






Bugs are tracked on `GitHub Issues
<https://github.com/OCA/stock-logistics-workflow/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
-------











### Contributors






* Alexis de Lattre <alexis.delattre@akretion.com>
* Eficent Business and IT Consulting Services S.L. <contact@eficent.com>
* Serpent Consulting Services Pvt. Ltd. <support@serpentcs.com>

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
