[![Build Status](https://travis-ci.org/zeroincombenze/stock-logistics-workflow.svg?branch=9.0)](https://travis-ci.org/zeroincombenze/stock-logistics-workflow)
[![license agpl](https://img.shields.io/badge/licence-AGPL--3-blue.svg)](http://www.gnu.org/licenses/agpl-3.0.html)
[![Coverage Status](https://coveralls.io/repos/github/zeroincombenze/stock-logistics-workflow/badge.svg?branch=9.0)](https://coveralls.io/github/zeroincombenze/stock-logistics-workflow?branch=9.0)
[![codecov](https://codecov.io/gh/zeroincombenze/stock-logistics-workflow/branch/9.0/graph/badge.svg)](https://codecov.io/gh/zeroincombenze/stock-logistics-workflow/branch/9.0)
[![OCA_project](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-oca-9.svg)](https://github.com/OCA/stock-logistics-workflow/tree/9.0)
[![Tech Doc](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-9.svg)](http://wiki.zeroincombenze.org/en/Odoo/9.0/dev)
[![Help](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-9.svg)](http://wiki.zeroincombenze.org/en/Odoo/9.0/man/LO)
[![try it](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-9.svg)](http://erp9.zeroincombenze.it)












































































[![en](http://www.shs-av.com/wp-content/en_US.png)](http://wiki.zeroincombenze.org/it/Odoo/7.0/man)

Stock Ownership Availability Rules
==================================

This module extends the core behaviour to manage ownership of stock. It is
useful when we want to keep stock that belongs to someone other than our
company.

This functionality is partially implemented in Odoo, with some missing
behaviour (e.g. it will silently deliver someone else's stock if that's all
we've got).

The purpose of this module is also to add tests that are missing in the Odoo
core.

With this module, the owner of quants becomes required, and is set by default
as follows:

- If the location of the quant has a partner, it is used.
- Otherwise, if the location of the quant has a company, the related partner is
  used.
- Otherwise, the partner related to the default company for quants is used.

The tests make sure that the quants reservation always respect owners:

- Outgoing pickings without owner or with company owner only reserve quants
  with company owner, otherwise they remain unreserved.
- Outgoing pickings with owner only reserve quants with the same owner,
  otherwise they remain unreserved.

To understand stock owners more easily, now the "On Hand" button on the product
form view opens a stock view grouped by location and owner (instead of location
only).

Partially related to this is issue https://github.com/odoo/odoo/issues/4136.


Installation
------------





Configuration
-------------





Usage
-----






Known issues / Roadmap
----------------------





Bug Tracker
-----------





Credits
-------










### Contributors






* Leonardo Pistone <leonardo.pistone@camptocamp.com>

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
