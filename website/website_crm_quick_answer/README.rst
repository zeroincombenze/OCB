[![Build Status](https://travis-ci.org/zeroincombenze/website.svg?branch=9.0)](https://travis-ci.org/zeroincombenze/website)
[![license agpl](https://img.shields.io/badge/licence-AGPL--3-blue.svg)](http://www.gnu.org/licenses/agpl-3.0.html)
[![Coverage Status](https://coveralls.io/repos/github/zeroincombenze/website/badge.svg?branch=9.0)](https://coveralls.io/github/zeroincombenze/website?branch=9.0)
[![codecov](https://codecov.io/gh/zeroincombenze/website/branch/9.0/graph/badge.svg)](https://codecov.io/gh/zeroincombenze/website/branch/9.0)
[![OCA_project](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-oca-9.svg)](https://github.com/OCA/website/tree/9.0)
[![Tech Doc](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-9.svg)](http://wiki.zeroincombenze.org/en/Odoo/9.0/dev)
[![Help](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-9.svg)](http://wiki.zeroincombenze.org/en/Odoo/9.0/man/)
[![try it](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-9.svg)](http://erp9.zeroincombenze.it)






















































































































































[![en](http://www.shs-av.com/wp-content/en_US.png)](http://wiki.zeroincombenze.org/it/Odoo/7.0/man)

    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

Quick answer for website contact form
=====================================

This module was written to extend the functionality of the website contact form
to support sending the interested contact an automatic welcome email and allow
you to customize it.

Installation
------------










Configuration
-------------











To configure this module, you need to:

* Go to *Settings > Technical > Automation > Automated actions > Quick response
  to website contact form* and edit anything there.

Quicker way to just change the email template (something that most likely you
will want to do):

* Go to *Settings > Technical > Email > Templates*
* Edit the template called *Quick response to website contact form*.

The email response will be sent the next time the *Email Queue Manager* is run.
To choose how often it runs:

* Go to *Settings > Technical > Automation > Scheduled Actions > Email Queue
  Manager > Edit*.

Usage
-----












=====

To use this module, you need to:

* Have an email address in your main company. It will be used as sender
  address.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/186/9.0

Known issues / Roadmap
----------------------











* The default template is quite basic, you should change that.
* The website form patch found in ``models/crm_lead.py`` was `proposed to Odoo
  and they rejected it <https://github.com/odoo/odoo/pull/15528>`_, so it
  must be maintained here until Odoo 11.0, where it will not be needed anymore.

Bug Tracker
-----------











Bugs are tracked on `GitHub Issues
<https://github.com/OCA/website/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
-------





















### Contributors











* Rafael Blasco <rafael.blasco@tecnativa.com>
* Jairo Llopis <jairo.llopis@tecnativa.com>

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
