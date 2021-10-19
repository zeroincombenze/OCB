[![Build Status](https://travis-ci.org/zeroincombenze/bank-payment.svg?branch=9.0)](https://travis-ci.org/zeroincombenze/bank-payment)
[![license agpl](https://img.shields.io/badge/licence-AGPL--3-blue.svg)](http://www.gnu.org/licenses/agpl-3.0.html)
[![Coverage Status](https://coveralls.io/repos/github/zeroincombenze/bank-payment/badge.svg?branch=9.0)](https://coveralls.io/github/zeroincombenze/bank-payment?branch=9.0)
[![codecov](https://codecov.io/gh/zeroincombenze/bank-payment/branch/9.0/graph/badge.svg)](https://codecov.io/gh/zeroincombenze/bank-payment/branch/9.0)
[![OCA_project](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-oca-9.svg)](https://github.com/OCA/bank-payment/tree/9.0)
[![Tech Doc](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-9.svg)](http://wiki.zeroincombenze.org/en/Odoo/9.0/dev)
[![Help](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-9.svg)](http://wiki.zeroincombenze.org/en/Odoo/9.0/man/FI)
[![try it](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-9.svg)](http://erp9.zeroincombenze.it)












































































[![en](http://www.shs-av.com/wp-content/en_US.png)](http://wiki.zeroincombenze.org/it/Odoo/7.0/man)

   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License AGPL-3

Batch reconciliation for transfer lines created in payment orders
=================================================================

This module allows to process with the connector technology the heavy task of
reconciliation of the receivable/payable journal entries of a payment order
against the created entries in transfer accounts.

This approach provides many advantages, similar to the ones we get
using that connector for e-commerce:

- Asynchronous: the operation is done in background, and users can
  continue to work.
- Dedicated workers: the queued jobs are performed by specific workers
  (processes). This is good for a long task, since the main workers are
  busy handling HTTP requests and can be killed if operations take
  too long, for example.
- Multiple transactions: this is an operation that doesn't need to be
  atomic, and if a line out of 100,000 fails, it is possible to catch
  it, see the error message, and fix the situation. Meanwhile, all
  other jobs can proceed.

Inspired on *account_move_batch_validate* module from Camptocamp and ACSONE.

Installation
------------






This module requires the *connector* module, hosted on
`OCA/connector <https://github.com/OCA/connector>`_

Configuration
-------------






This will only work for payment modes that have a transfer account set.

Usage
-----






=====

When exporting the payment order, click on *Validate* to generate the transfer
move. One connector job will be created for each payment line for a deferred
conciliation of this line.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/173/9.0

Known issues / Roadmap
----------------------





Bug Tracker
-----------






Bugs are tracked on `GitHub Issues
<https://github.com/OCA/bank-payment/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
-------











### Contributors






* Pedro M. Baeza <pedro.baeza@tecnativa.com>
* Sergio Teruel <sergio.teruel@tecnativa.com>

### Funders

### Maintainer










.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

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
