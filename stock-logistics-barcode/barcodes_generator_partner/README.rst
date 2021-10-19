[![Build Status](https://travis-ci.org/zeroincombenze/stock-logistics-barcode.svg?branch=9.0)](https://travis-ci.org/zeroincombenze/stock-logistics-barcode)
[![license agpl](https://img.shields.io/badge/licence-AGPL--3-blue.svg)](http://www.gnu.org/licenses/agpl-3.0.html)
[![Coverage Status](https://coveralls.io/repos/github/zeroincombenze/stock-logistics-barcode/badge.svg?branch=9.0)](https://coveralls.io/github/zeroincombenze/stock-logistics-barcode?branch=9.0)
[![codecov](https://codecov.io/gh/zeroincombenze/stock-logistics-barcode/branch/9.0/graph/badge.svg)](https://codecov.io/gh/zeroincombenze/stock-logistics-barcode/branch/9.0)
[![OCA_project](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-oca-9.svg)](https://github.com/OCA/stock-logistics-barcode/tree/9.0)
[![Tech Doc](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-9.svg)](http://wiki.zeroincombenze.org/en/Odoo/9.0/dev)
[![Help](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-9.svg)](http://wiki.zeroincombenze.org/en/Odoo/9.0/man/LO)
[![try it](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-9.svg)](http://erp9.zeroincombenze.it)












































































[![en](http://www.shs-av.com/wp-content/en_US.png)](http://wiki.zeroincombenze.org/it/Odoo/7.0/man)

   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

Generate Barcodes for Partners
==============================

This module expends Odoo functionality, allowing user to generate barcode
depending on a given barcode rule for Partners.

For exemple, a typical pattern for partners is  "042........." that means
that:
* the EAN13 code will begin by '042'
* followed by 0 digits (named Barcode Base in this module)
* a 13 digit control

With this module, it is possible to:

* Affect a pattern (barcode.rule) to a res.partner

* Define a Barcode base: 
    * manually, if the base of the barcode must be set by a user. (typically an
      internal code defined in your company)
    * automaticaly by a sequence, if you want to let Odoo to increment a
      sequence. (typical case of a customer number incrementation)

* Generate a barcode, based on the defined pattern and the barcode base

Installation
------------





Configuration
-------------






To configure this module, see the 'Configuration' Section of the description
of the module 'barcodes_generator_abstract'

Usage
-----






=====

To use this module, you need to:

* Go to a Product form (or a template form):

1 for manual generation
    * Set a Barcode Rule
    * Set a Barcode Base
    * click on the button 'Generate Barcode (Using Barcode Rule)'

2 for automatic generation
    * Set a Barcode Rule
    * click on the button 'Generate Base (Using Sequence)'
    * click on the button 'Generate Barcode (Using Barcode Rule)'

.. image:: /barcodes_generator/static/description/res_partner_sequence_generation.png

Try this module on Runbot

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/150/9.0

Known issues / Roadmap
----------------------






Dependency to point_of_sale is required because barcode field, defined in 'base'
module (in the res.partner model), is defined in a 'point_of_sale' view.

It's a relative problem, because barcodes generation for partners will occures
mostly in a Point of Sale context, to give barcodes to customers.

You could comment 'point_of_sale' dependencies if you want to use this module
without point of sale installed.

Bug Tracker
-----------






Bugs are tracked on `GitHub Issues
<https://github.com/OCA/pos/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
-------






Images

* Icon of the module is based on the Oxygen Team work and is under LGPL licence:
  http://www.iconarchive.com/show/oxygen-icons-by-oxygen-icons.org.html






### Contributors






* Sylvain LE GAL (https://twitter.com/legalsylvain)

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
