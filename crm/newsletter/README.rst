[![Build Status](https://travis-ci.org/zeroincombenze/crm.svg?branch=9.0)](https://travis-ci.org/zeroincombenze/crm)
[![license agpl](https://img.shields.io/badge/licence-AGPL--3-blue.svg)](http://www.gnu.org/licenses/agpl-3.0.html)
[![Coverage Status](https://coveralls.io/repos/github/zeroincombenze/crm/badge.svg?branch=9.0)](https://coveralls.io/github/zeroincombenze/crm?branch=9.0)
[![codecov](https://codecov.io/gh/zeroincombenze/crm/branch/9.0/graph/badge.svg)](https://codecov.io/gh/zeroincombenze/crm/branch/9.0)
[![OCA_project](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-oca-9.svg)](https://github.com/OCA/crm/tree/9.0)
[![Tech Doc](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-9.svg)](http://wiki.zeroincombenze.org/en/Odoo/9.0/dev)
[![Help](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-9.svg)](http://wiki.zeroincombenze.org/en/Odoo/9.0/man/)
[![try it](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-9.svg)](http://erp9.zeroincombenze.it)










































[![en](http://www.shs-av.com/wp-content/en_US.png)](http://wiki.zeroincombenze.org/it/Odoo/7.0/man)

Newsletters
===========
With this addon, you can send HTML-formatted mass emails to your customers.
While it was developed with primarily newsletters in mind, it works for
arbitrary objects and arbitrary content.

This is something else than the mass_mailing module, which is geared very much
on marketing campaigns with appropriate language and measuring tools.

Installation
------------






Under Sales/Configuration/Newsletter types, review the default one or create a
new one. You'll have to fill in a name, a model, a domain expression on that
model, an email template (have a look a the default newsletter type's email
template to see how this might look like) and the address that should show up
as the sender's address.

If you fill in a group in the type's groups-field, only users which are a
member of said group are allowed to send a newsletter of this type. See below
for details.

Finally, click 'Show recipient objects' to check the list of records that will
receive a newsletter of this type. We work with dynamic selections here, so
this list ist not fixed and will be evaluated every time you send a newsletter.

Configuration
-------------






There are three groups defined:

newsletter editor
  A user who can create a newsletter and add/edit topics

newsletter sender
  A user who may send newsletters. Note that if a newsletter type is
  restricted to certain groups, the user has to be a newsletter sender and
  be a member of one of the groups given in the newsletter type

newsletter manager
  A user who may edit newsletter types

Note that the groups are listed in order of inheritance, so a newsletter sender
always also is an editor and a manager is a sender as well as an editor.

Usage
-----






=====

After a newsletter type is configured, the handling is pretty straightworfard:
Go to Sales/Newsletters/Newsletters and create a new one. Choose the type you
configured before and fill in a subject.

Often, a template will be chosen that enforces a certain layout for different
subsections of your text. That's why the text is broken up into an intro, an
outro and topics with optional heading in between. This way, you can put most
of the layout into the template and leave only the interesting layout to your
users.

A note on images: If you upload an image via the editor, it will be embedded
as dataurl into the resulting email. This is good for your customers' privacy,
but bad for bandwidth, so take care to chose reasonable image sizes.

It is mandatory that you click on 'Preview' before you are allowed to finally
send the newsletter. The sending process uses Odoo's standard email queue.

For further information, please visit:

 * https://www.odoo.com/forum/help-1

Known issues / Roadmap
----------------------






 * a glue module between this and mass_mailing would be nice

Bug Tracker
-----------





Credits
-------











### Contributors






* Holger Brunn <hbrun@therp.nl>

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
which distributes and promotes **Odoo** ready-to-use on its own cloud infrastructure.
[Zeroincombenze® distribution](http://wiki.zeroincombenze.org/en/Odoo)
is mainly designed for Italian law and markeplace.
Everytime, every Odoo DB and customized code can be deployed on local server too.

[//]: # (end copyright)

[//]: # (addons)

[//]: # (end addons)

[![chat with us](https://www.shs-av.com/wp-content/chat_with_us.gif)](https://tawk.to/85d4f6e06e68dd4e358797643fe5ee67540e408b)
