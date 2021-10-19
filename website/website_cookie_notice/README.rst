[![Build Status](https://travis-ci.org/zeroincombenze/website.svg?branch=9.0)](https://travis-ci.org/zeroincombenze/website)
[![license agpl](https://img.shields.io/badge/licence-AGPL--3-blue.svg)](http://www.gnu.org/licenses/agpl-3.0.html)
[![Coverage Status](https://coveralls.io/repos/github/zeroincombenze/website/badge.svg?branch=9.0)](https://coveralls.io/github/zeroincombenze/website?branch=9.0)
[![codecov](https://codecov.io/gh/zeroincombenze/website/branch/9.0/graph/badge.svg)](https://codecov.io/gh/zeroincombenze/website/branch/9.0)
[![OCA_project](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-oca-9.svg)](https://github.com/OCA/website/tree/9.0)
[![Tech Doc](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-9.svg)](http://wiki.zeroincombenze.org/en/Odoo/9.0/dev)
[![Help](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-9.svg)](http://wiki.zeroincombenze.org/en/Odoo/9.0/man/)
[![try it](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-9.svg)](http://erp9.zeroincombenze.it)






















































































































































[![en](http://www.shs-av.com/wp-content/en_US.png)](http://wiki.zeroincombenze.org/it/Odoo/7.0/man)

    :alt: License: AGPL-3

Cookie notice
=============

This module adds the cookie notice, according to the `european cookie law
<http://eur-lex.europa.eu/LexUriServ/LexUriServ.do?uri=CELEX:32002L0058:en:HTML>`_,
to your website.

Installation
------------










Configuration
-------------











To change the cookie message:

* Go to *Settings > Technical > User Interface > Views*.
* Search for the view called *cookiebanner*.
* Change as you wish. Remember that you will probably lose translations then.

If you are developing a theme for Odoo, remember that this message has the
``cc-cookies`` class. You can style it at will too.

Known Issues / Roadmap

* If you are using this module in version < 8.0.2.0.0 and update it, any other
  module that modifies the ``res.company`` view will break in the next update
  if Odoo decides to update it before this one. To avoid that:

  1. Stop your server.
  2. Update only this module: ``odoo.py -u website_cookie_notice``.
  3. Stop your server.
  4. Update all other modules: ``odoo.py -u all``.
  5. Start your server.

* Before version 8.0.2.0.0 of this module, users had the ability to configure
  the message functionality and appearance from the main company form.

  Now, the message is generated in a view. This means that after upgrading to
  >= 8.0.2.0.0 you will lose your previous customized messages. If you want to
  customize it, please follow steps in the configuration section.

Usage
-----












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





















### Contributors











* Lorenzo Battistini <lorenzo.battistini@agilebg.com>
* Rafael Blasco <rafabn@antiun.com>
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

To contribute to this module, please visit http://odoo-community.org.

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
