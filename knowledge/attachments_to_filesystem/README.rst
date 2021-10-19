[![Build Status](https://travis-ci.org/zeroincombenze/knowledge.svg?branch=9.0)](https://travis-ci.org/zeroincombenze/knowledge)
[![license agpl](https://img.shields.io/badge/licence-AGPL--3-blue.svg)](http://www.gnu.org/licenses/agpl-3.0.html)
[![Coverage Status](https://coveralls.io/repos/github/zeroincombenze/knowledge/badge.svg?branch=9.0)](https://coveralls.io/github/zeroincombenze/knowledge?branch=9.0)
[![codecov](https://codecov.io/gh/zeroincombenze/knowledge/branch/9.0/graph/badge.svg)](https://codecov.io/gh/zeroincombenze/knowledge/branch/9.0)
[![OCA_project](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-oca-9.svg)](https://github.com/OCA/knowledge/tree/9.0)
[![Tech Doc](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-9.svg)](http://wiki.zeroincombenze.org/en/Odoo/9.0/dev)
[![Help](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-9.svg)](http://wiki.zeroincombenze.org/en/Odoo/9.0/man/)
[![try it](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-9.svg)](http://erp9.zeroincombenze.it)












































































[![en](http://www.shs-av.com/wp-content/en_US.png)](http://wiki.zeroincombenze.org/it/Odoo/7.0/man)

Introduction
============
This addon allows to automatically move existing attachments to the file
system.

Installation
------------





Configuration
-------------





If it doesn't exist, the module creates a parameter `ir_attachment.location`
with value `file`. This will make new attachments end up in your
data path (the odoo configuration value `data_dir`) in a subdirectory called
`filestore`.

Then it will create a cron job that does the actual transfer and schedule it
for 01:42 at night in the installing user's time zone. The cronjob will do a
maximum of 10000 conversions per run and is run every night.
The limit is configurable with the parameter `attachments_to_filesystem.limit`.

After all attachments are migrated (the log will show then `moving 0
attachments to filestore`), you can disable or delete the cronjob.

If you need to run the migration synchronously during install, set the
parameter `attachments_to_filesystem.move_during_init` *before* installing this
addon.

Usage
-----






Known issues / Roadmap
----------------------





Bug Tracker
-----------





Credits
-------











### Contributors






* Holger Brunn <hbrunn@therp.nl>

Icon
----

http://commons.wikimedia.org/wiki/File:Crystal_Clear_app_harddrive.png

### Funders

### Maintainer










.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

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
