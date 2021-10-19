[![Build Status](https://travis-ci.org/zeroincombenze/knowledge.svg?branch=9.0)](https://travis-ci.org/zeroincombenze/knowledge)
[![license agpl](https://img.shields.io/badge/licence-AGPL--3-blue.svg)](http://www.gnu.org/licenses/agpl-3.0.html)
[![Coverage Status](https://coveralls.io/repos/github/zeroincombenze/knowledge/badge.svg?branch=9.0)](https://coveralls.io/github/zeroincombenze/knowledge?branch=9.0)
[![codecov](https://codecov.io/gh/zeroincombenze/knowledge/branch/9.0/graph/badge.svg)](https://codecov.io/gh/zeroincombenze/knowledge/branch/9.0)
[![OCA_project](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-oca-9.svg)](https://github.com/OCA/knowledge/tree/9.0)
[![Tech Doc](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-9.svg)](http://wiki.zeroincombenze.org/en/Odoo/9.0/dev)
[![Help](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-9.svg)](http://wiki.zeroincombenze.org/en/Odoo/9.0/man/)
[![try it](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-9.svg)](http://erp9.zeroincombenze.it)












































































[![en](http://www.shs-av.com/wp-content/en_US.png)](http://wiki.zeroincombenze.org/it/Odoo/7.0/man)

Reindex documents
=================

This module allows you to reindex documents in case they were uploaded when the right configuration for indexation was missing.

Installation
------------





Configuration
-------------





Usage
-----






=====

To reindex a single document, open its form and click the `Reindex document` button.

To reindex all documents, go to Settings / Configuration / Knowledge, check the box `Reindex all documents` or `Reindex all unindexed documents` and click apply. Those are done in the background, so watch your logs for the process to finish.

In a migration context, you might want to reindex all or unindexed documents. To achieve this, create a config parameter `document_reindex.reindex_unindexed_on_init` or `document_reindex.reindex_all_on_init` to have the reindexation run synchronously during installation of this module.

Known issues / Roadmap
----------------------





Bug Tracker
-----------





Credits
-------











### Contributors






* Holger Brunn <hbrunn@therp.nl>
* Icon courtesy of http://www.picol.org (refresh.svg) and https://github.com/odoo/odoo/blob/8.0/addons/knowledge/static/description/icon.png

### Funders

### Maintainer










.. image:: http://odoo-community.org/logo.png
    :alt: Odoo Community Association
    :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

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
