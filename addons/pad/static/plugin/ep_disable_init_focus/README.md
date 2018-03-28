[![Build Status](https://travis-ci.org/zeroincombenze/ep_disable_init_focus.svg?branch=10.0)](https://travis-ci.org/zeroincombenze/ep_disable_init_focus)
[![license agpl](https://img.shields.io/badge/licence-AGPL--3-blue.svg)](http://www.gnu.org/licenses/agpl-3.0.html)
[![Coverage Status](https://coveralls.io/repos/github/zeroincombenze/ep_disable_init_focus/badge.svg?branch=10.0)](https://coveralls.io/github/zeroincombenze/ep_disable_init_focus?branch=10.0)
[![codecov](https://codecov.io/gh/zeroincombenze/ep_disable_init_focus/branch/10.0/graph/badge.svg)](https://codecov.io/gh/zeroincombenze/ep_disable_init_focus/branch/10.0)
[![OCA_project](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-oca-10.svg)](https://github.com/OCA/ep_disable_init_focus/tree/10.0)
[![Tech Doc](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-10.svg)](http://wiki.zeroincombenze.org/en/Odoo/10.0/dev)
[![Help](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-10.svg)](http://wiki.zeroincombenze.org/en/Odoo/10.0/man/)
[![try it](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-10.svg)](http://erp10.zeroincombenze.it)


[![en](http://www.shs-av.com/wp-content/en_US.png)](http://wiki.zeroincombenze.org/it/Odoo/7.0/man)

Readme
======

`ep_disable_init_focus` is a very simple
[Etherpad-lite](https://github.com/ether/etherpad-lite) plugin, which disable
the focus on the pad content after its loading.

Rationale

Etherpad-lite autofocus can be annoying to end-users when it is used in Odoo's
"pad" widget, because it will override web client focus rules. This plugin is
design to get rid of this behavior.


Installation
------------

1. Stop your Etherpad-lite server.
2. Copy the `ep_disabl_init_focus` folder into the `node_modules` folder of
   your Etherpad-lite installation.
3. in the folder of your Etherpad-lite installation, run this command to
   install the plugin:

    ```sh
    npm install node_modules/ep_disable_init_focus/
    ```
4. Restart the Etherpad-lite server.

[//]: # (copyright)

----

**Odoo** is a trademark of [Odoo S.A.](https://www.odoo.com/) (formerly OpenERP, formerly TinyERP)

**OCA**, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

**zeroincombenze®** is a trademark of [SHS-AV s.r.l.](http://www.shs-av.com/)
which distributes and promotes **Odoo** ready-to-use on its own cloud infrastructure.
[Zeroincombenze® distribution](http://wiki.zeroincombenze.org/en/Odoo)
is mainly designed for Italian law and markeplace.
Everytime, every Odoo DB and customized code can be deployed on local server too.

[//]: # (end copyright)

[//]: # (addons)

[//]: # (end addons)

[![chat with us](https://www.shs-av.com/wp-content/chat_with_us.gif)](https://tawk.to/85d4f6e06e68dd4e358797643fe5ee67540e408b)
