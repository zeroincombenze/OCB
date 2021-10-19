[![Build Status](https://travis-ci.org/zeroincombenze/knowledge.svg?branch=9.0)](https://travis-ci.org/zeroincombenze/knowledge)
[![license agpl](https://img.shields.io/badge/licence-AGPL--3-blue.svg)](http://www.gnu.org/licenses/agpl-3.0.html)
[![Coverage Status](https://coveralls.io/repos/github/zeroincombenze/knowledge/badge.svg?branch=9.0)](https://coveralls.io/github/zeroincombenze/knowledge?branch=9.0)
[![codecov](https://codecov.io/gh/zeroincombenze/knowledge/branch/9.0/graph/badge.svg)](https://codecov.io/gh/zeroincombenze/knowledge/branch/9.0)
[![OCA_project](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-oca-9.svg)](https://github.com/OCA/knowledge/tree/9.0)
[![Tech Doc](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-9.svg)](http://wiki.zeroincombenze.org/en/Odoo/9.0/dev)
[![Help](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-9.svg)](http://wiki.zeroincombenze.org/en/Odoo/9.0/man/)
[![try it](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-9.svg)](http://erp9.zeroincombenze.it)












































































[![en](http://www.shs-av.com/wp-content/en_US.png)](http://wiki.zeroincombenze.org/it/Odoo/7.0/man)

   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

Document Page Approval
======================

This module adds a workflow to approve page modification and show the approved
version by default.

Installation
------------






Makes the document page approval available from where some users can approved the modifications
made by others users in documents that required approvement.

Configuration
-------------






No configuration required

Usage
-----






=====

To use this module, you need to:

* Set a valid email address on the company settings.
* go to knowledge > Categories.
* Create a new page category and set an approver group. Make sure users
  belonging to that group have valid email addresses.
* go to knowledge > Pages
* Create a new page and choose the previously created category.
* A notification is sent to the group with a link to the page history to
  review.
* Depending on the review, the page history is approved or not.
* Users reading the page see the last approved version.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/118/9.0

Known issues / Roadmap
----------------------







Bug Tracker
-----------






Bugs are tracked on `GitHub Issues <https://github.com/OCA/
knowledge/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback `here <https://github.com/OCA/knowledge/issues/new?body=module:%20document_page_approval%0Aversion:%209.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
-------











### Contributors






* Odoo SA <info@odoo.com>
* Savoir-faire Linux <support@savoirfairelinux.com>
* Gervais Naoussi <gervaisnaoussi@gmail.com>

### Funders

### Maintainer










.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.

Changelog

v9.0.1.0.0

Here are the modification that have been done:

* The module does no depends anymore on email_template but on mail module

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
