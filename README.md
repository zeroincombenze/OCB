[![Build Status](https://travis-ci.org/zeroincombenze/OCB.svg?branch=7.0)](https://travis-ci.org/zeroincombenze/OCB)
[![license agpl](https://img.shields.io/badge/licence-AGPL--3-blue.svg)](http://www.gnu.org/licenses/agpl-3.0.html)
[![Coverage Status](https://coveralls.io/repos/github/zeroincombenze/OCB/badge.svg?branch=7.0)](https://coveralls.io/github/zeroincombenze/OCB?branch=7.0)
[![codecov](https://codecov.io/gh/zeroincombenze/OCB/branch/7.0/graph/badge.svg)](https://codecov.io/gh/zeroincombenze/OCB/branch/7.0)
[![OCA_project](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-oca-7.svg)](https://github.com/OCA/OCB/tree/7.0)
[![Tech Doc](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-7.svg)](http://wiki.zeroincombenze.org/en/Odoo/7.0/dev)
[![Help](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-7.svg)](http://wiki.zeroincombenze.org/en/Odoo/7.0/man/)
[![try it](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-7.svg)](http://erp7.zeroincombenze.it)


[![en](http://www.shs-av.com/wp-content/en_US.png)](http://wiki.zeroincombenze.org/it/Odoo/7.0/man)

Odoo is an OpenSource/Free software Enterprise Resource Planning and
====================================================================
Customer Relationship Management software. More info at:

    http://www.odoo.com

Installation
------------

Add the the apt repository

    deb http://nightly.odoo.com/7.0/nightly/deb/ ./

in your source.list and type:

    $ sudo apt-get update
    $ sudo apt-get install openerp

Or download the deb file and type:

    $ sudo dpkg -i <openerp-deb-filename>
    $ sudo apt-get install install -f


Install the required dependencies:

    $ yum install python
    $ easy_install pip
    $ pip install .....

Install the openerp rpm

    $ rpm -i openerp-VERSION.rpm


    Check the notes in setup.py


Setting up your first database

Point your browser to http://localhost:8069/ and click "Manage Databases", the
default master password is "admin".

Detailed System Requirements

The dependencies are listed in setup.py

For Luxembourg localization, you also need:

 pdftk (http://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/)

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
