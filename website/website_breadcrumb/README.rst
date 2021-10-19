[![Build Status](https://travis-ci.org/zeroincombenze/website.svg?branch=9.0)](https://travis-ci.org/zeroincombenze/website)
[![license agpl](https://img.shields.io/badge/licence-AGPL--3-blue.svg)](http://www.gnu.org/licenses/agpl-3.0.html)
[![Coverage Status](https://coveralls.io/repos/github/zeroincombenze/website/badge.svg?branch=9.0)](https://coveralls.io/github/zeroincombenze/website?branch=9.0)
[![codecov](https://codecov.io/gh/zeroincombenze/website/branch/9.0/graph/badge.svg)](https://codecov.io/gh/zeroincombenze/website/branch/9.0)
[![OCA_project](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-oca-9.svg)](https://github.com/OCA/website/tree/9.0)
[![Tech Doc](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-9.svg)](http://wiki.zeroincombenze.org/en/Odoo/9.0/dev)
[![Help](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-9.svg)](http://wiki.zeroincombenze.org/en/Odoo/9.0/man/)
[![try it](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-9.svg)](http://erp9.zeroincombenze.it)






















































































































































[![en](http://www.shs-av.com/wp-content/en_US.png)](http://wiki.zeroincombenze.org/it/Odoo/7.0/man)

.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

Website Breadcrumbs
===================

This module allows you to have breadcrumbs in any page of your website.
But if an URL is not present in a menu (as indicated in the Configuration section), no breadcrumbs will display.

Installation
------------










Configuration
-------------











To configure the shown breadcrumbs, you need to:

* Go to *Website Admin > Configuration* and click on "Configure website menus".
* Edit any menu there.

Keep in mind that:

* This module will try to match **exactly** the URL in the menu item with the
  one you are browsing.
* If it finds no match, breadcrumbs will not be shown.
* If it finds several matches, only the first one will be used.
* Using more than 1 submenu for the website top menu will probably make it
  unusable. In case you need that granularity, you will have to create a
  separate top menu for managing your breadcrumbs.
* Breadcrumbs use the menu name, **not the page name**, except for the top menu
  item, which will appear as *Home* and point to ``/`` unless you specify an
  URL for it.

Usage
-----












=====

To use this module, you need to:

* Log in.
* Go to your homepage.
* Go to *Customize* menu.
* Enable *Breadcrumbs* (it is enabled by default).

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/186/9.0


Theming

* If you want to use this module in a theme but you do not like where it is
  rendered, you can simply disable it in the top menu and add in you own
  layout a ``<t t-call="website_breadcrumb.breadcrumb"/>`` element.

Known issues / Roadmap
----------------------










Bug Tracker
-----------











Bugs are tracked on `GitHub Issues
<https://github.com/OCA/website/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
-------











Images

* Jairo Llopis: Icon.











### Contributors











* Jairo Llopis <yajo.sk8@gmail.com>

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
