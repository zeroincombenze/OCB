
===================================
|icon| Invoicing/account 10.0.1.1.2
===================================

**Send Invoices and Track Payments**

.. |icon| image:: https://raw.githubusercontent.com/zeroincombenze/addons/10.0/account/static/description/icon.png


.. contents::



Overview | Panoramica
=====================

|en| Invoicing & Payments
=========================
The specific and easy-to-use Invoicing system in Odoo allows you to keep track of your
accounting, even when you are not an accountant. It provides an easy way to follow up
on your vendors and customers.

You could use this simplified accounting in case you work with an (external) account
to keep your books, and you still want to keep track of payments.
This module also offers you an easy method of registering payments, without
having to encode complete abstracts of account.

Odoo Accounting
---------------

The Odoo <a href="https://www.odoo.com/page/accounting">Open Source Accounting</a> app
allows a better way to collaborate with your accountants, your customers and control
your suppliers.

Activate features on demand, from integrated analytic accounting to budget,
assets and multiple companies consolidation.

A Smart User Interface
----------------------

Record transactions in a few clicks and easily manage all financial activities
in one place. Odoo's user interface is designed with productivity in mind.

A Better Way To Work – Together
-------------------------------

Share access to your latest business numbers with your team and your accountant
– so everyone is up to speed. From work, home or on the go.

Connect Your Bank Accounts
--------------------------

Import your bank statements and reconcile them in just a few clicks. Prepare
payment orders based on your supplier invoices and payment terms.

Electronic invoicing and automated follow-ups
---------------------------------------------

Create and send professional invoices & get paid online. Get rid of the stress
of having to constantly remind your debtors. Simply set-up and automate
follow-ups to get paid quickly.

Sales Integration
-----------------

Automatically create invoices from sales orders, delivery orders or base them
on time and material. Re-invoice expenses on projects to your customer in just
a few clicks.


Purchase Integration
--------------------

Control supplier invocies based on purchase orders. Get real-time inventory
valuation reports automatically posted in your accounts.

Multi-Level Analytic Accounting
-------------------------------

Integrate your analytic accounting operations with timesheets, projects,
invoices, expenses, etc. No need to record transactions, all analytic entries
are posted automatically following your business rules.

Everything you need to grow
---------------------------

Manage your assets, track expenses, control budgets, multi-level analytic
accounting; Odoo has all the features you need to sustain all your business
activities.

Scale With Your Organization
----------------------------

Odoo supports multiple currencies, multiple users with different access rights,
multiple companies with real time consolidation and unlimited analytic plans.


|

|it| Contabilità e pagamenti
============================

Modulo per la gestione della fatturazione, della contabilità e dei pagamenti fatture.
Permette anche di emettere gli estratti conto clienti.


|

Getting started | Primi passi
=============================

|Try Me|


|

Installation | Installazione
----------------------------


+---------------------------------+------------------------------------------+
| |en|                            | |it|                                     |
+---------------------------------+------------------------------------------+
| These instructions are just an  | Istruzioni di esempio valide solo per    |
| example; use on Linux CentOS 7+ | distribuzioni Linux CentOS 7+,           |
| Ubuntu 14+ and Debian 8+        | Ubuntu 14+ e Debian 8+                   |
|                                 |                                          |
| Installation is built with:     | L'installazione è costruita con:         |
+---------------------------------+------------------------------------------+
| `Zeroincombenze Tools <https://zeroincombenze-tools.readthedocs.io/>`__ |
+---------------------------------+------------------------------------------+
| Suggested deployment is:        | Posizione suggerita per l'installazione: |
+---------------------------------+------------------------------------------+
| $HOME/10.0 |
+----------------------------------------------------------------------------+

::

    cd $HOME
    # *** Tools installation & activation ***
    # Case 1: you have not installed zeroincombenze tools
    git clone https://github.com/zeroincombenze/tools.git
    cd $HOME/tools
    ./install_tools.sh -pT
    source $HOME/devel/activate_tools
    # Case 2: you have already installed zeroincombenze tools
    cd $HOME/tools
    ./install_tools.sh -UT
    source $HOME/devel/activate_tools
    # *** End of tools installation or upgrade ***
    # Odoo repository installation; OCB repository must be installed
    deploy_odoo clone -r addons -b 10.0 -G zero -p $HOME/10.0
    # Upgrade virtual environment
    vem amend $HOME/10.0/venv_odoo

From UI: go to:

* |menu| Setting > Activate Developer mode
* |menu| Apps > Update Apps List
* |menu| Setting > Apps |right_do| Select **account** > Install


|

Upgrade | Aggiornamento
-----------------------


::

    cd $HOME
    # *** Tools installation & activation ***
    # Case 1: you have not installed zeroincombenze tools
    git clone https://github.com/zeroincombenze/tools.git
    cd $HOME/tools
    ./install_tools.sh -pT
    source $HOME/devel/activate_tools
    # Case 2: you have already installed zeroincombenze tools
    cd $HOME/tools
    ./install_tools.sh -UT
    source $HOME/devel/activate_tools
    # *** End of tools installation or upgrade ***
    # Odoo repository upgrade
    deploy_odoo update -r addons -b 10.0 -G zero -p $HOME/10.0
    vem amend $HOME/10.0/venv_odoo
    # Adjust following statements as per your system
    sudo systemctl restart odoo

From UI: go to:

* |menu| Setting > Activate Developer mode
* |menu| Apps > Update Apps List
* |menu| Setting > Apps |right_do| Select **account** > Update


|

Support | Supporto
------------------


|Zeroincombenze| This module is supported by the `SHS-AV s.r.l. <https://www.zeroincombenze.it/>`__


|
|

Get involved | Ci mettiamo in gioco
===================================

Bug reports are welcome! You can use the issue tracker to report bugs,
and/or submit pull requests on `GitHub Issues
<https://github.com/zeroincombenze/addons/issues>`_.

In case of trouble, please check there if your issue has already been reported.

Proposals for enhancement
-------------------------


|en| If you have a proposal to change this module, you may want to send an email to <cc@shs-av.com> for initial feedback.
An Enhancement Proposal may be submitted if your idea gains ground.

|it| Se hai proposte per migliorare questo modulo, puoi inviare una mail a <cc@shs-av.com> per un iniziale contatto.


ChangeLog History | Cronologia modifiche
----------------------------------------

10.0.1.1.2 (2023-07-21)
~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] Avoid chrome 89 delegation / Miglioramento filtri ricerca
* [IMP] Supplier reference by year / Ricerca n. fattura fornitore limitato all'anno
* [QUA] Test coverage 44% (6041 / 3376)

10.0.1.1.1 (2016-10-03)
~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Odoo Odoo relase


|
|

Credits | Didascalie
====================

Copyright
---------

Odoo is a trademark of `Odoo S.A. <https://www.odoo.com/>`__ (formerly OpenERP)


|

Authors | Autori
----------------

* `Odoo S.A. <https://www.odoo.com>`__
* `SHS-AV s.r.l. <https://www.zeroincombenze.it>`__

Contributors | Contributi da
----------------------------

* Antonio Maria Vigliotti <antoniomaria.vigliotti@gmail.com>

Maintainer | Manutenzione
-------------------------

Antonio M. Vigliotti <antoniomaria.vigliotti@gmail.com>

|

----------------


|en| **zeroincombenze®** is a trademark of `SHS-AV s.r.l. <https://www.shs-av.com/>`__
which distributes and promotes ready-to-use **Odoo** on own cloud infrastructure.
`Zeroincombenze® distribution of Odoo <https://www.zeroincombenze.it/>`__
is mainly designed to cover Italian law and markeplace.

|it| **zeroincombenze®** è un marchio registrato da `SHS-AV s.r.l. <https://www.shs-av.com/>`__
che distribuisce e promuove **Odoo** pronto all'uso sulla propria infrastuttura.
La distribuzione `Zeroincombenze® <https://www.zeroincombenze.it/>`__ è progettata per le esigenze del mercato italiano.


|

This module is part of addons project.

Last Update / Ultimo aggiornamento: 2023-10-26

.. |Maturity| image:: https://img.shields.io/badge/maturity-Alfa-black.png
    :target: https://odoo-community.org/page/development-status
    :alt: 
.. |Build Status| image:: https://travis-ci.org/zeroincombenze/addons.svg?branch=10.0
    :target: https://travis-ci.com/zeroincombenze/addons
    :alt: github.com
.. |license gpl| image:: https://img.shields.io/badge/licence-LGPL--3-7379c3.svg
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3
.. |license opl| image:: https://img.shields.io/badge/licence-OPL-7379c3.svg
    :target: https://www.odoo.com/documentation/user/14.0/legal/licenses/licenses.html
    :alt: License: OPL
.. |Coverage Status| image:: https://coveralls.io/repos/github/zeroincombenze/addons/badge.svg?branch=10.0
    :target: https://coveralls.io/github/zeroincombenze/addons?branch=10.0
    :alt: Coverage
.. |Codecov Status| image:: https://codecov.io/gh/zeroincombenze/addons/branch/10.0/graph/badge.svg
    :target: https://codecov.io/gh/zeroincombenze/addons/branch/10.0
    :alt: Codecov
.. |Tech Doc| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-10.svg
    :target: https://wiki.zeroincombenze.org/en/Odoo/10.0/dev
    :alt: Technical Documentation
.. |Help| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-10.svg
    :target: https://wiki.zeroincombenze.org/it/Odoo/10.0/man
    :alt: Technical Documentation
.. |Try Me| image:: https://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-10.svg
    :target: https://erp10.zeroincombenze.it
    :alt: Try Me
.. |OCA Codecov| image:: https://codecov.io/gh/OCA/addons/branch/10.0/graph/badge.svg
    :target: https://codecov.io/gh/OCA/addons/branch/10.0
    :alt: Codecov
.. |Odoo Italia Associazione| image:: https://www.odoo-italia.org/images/Immagini/Odoo%20Italia%20-%20126x56.png
   :target: https://odoo-italia.org
   :alt: Odoo Italia Associazione
.. |Zeroincombenze| image:: https://avatars0.githubusercontent.com/u/6972555?s=460&v=4
   :target: https://www.zeroincombenze.it/
   :alt: Zeroincombenze
.. |en| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/flags/en_US.png
   :target: https://www.facebook.com/Zeroincombenze-Software-gestionale-online-249494305219415/
.. |it| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/flags/it_IT.png
   :target: https://www.facebook.com/Zeroincombenze-Software-gestionale-online-249494305219415/
.. |check| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/check.png
.. |no_check| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/no_check.png
.. |menu| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/menu.png
.. |right_do| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/right_do.png
.. |exclamation| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/exclamation.png
.. |warning| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/warning.png
.. |same| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/same.png
.. |late| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/late.png
.. |halt| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/halt.png
.. |info| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/awesome/info.png
.. |xml_schema| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/certificates/iso/icons/xml-schema.png
   :target: https://github.com/zeroincombenze/grymb/blob/master/certificates/iso/scope/xml-schema.md
.. |DesktopTelematico| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/certificates/ade/icons/DesktopTelematico.png
   :target: https://github.com/zeroincombenze/grymb/blob/master/certificates/ade/scope/Desktoptelematico.md
.. |FatturaPA| image:: https://raw.githubusercontent.com/zeroincombenze/grymb/master/certificates/ade/icons/fatturapa.png
   :target: https://github.com/zeroincombenze/grymb/blob/master/certificates/ade/scope/fatturapa.md
.. |chat_with_us| image:: https://www.shs-av.com/wp-content/chat_with_us.gif
   :target: https://t.me/Assitenza_clienti_powERP


