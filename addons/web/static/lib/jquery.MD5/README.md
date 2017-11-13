[![Build Status](https://travis-ci.org/zeroincombenze/jquery.MD5.svg?branch=7.0)](https://travis-ci.org/zeroincombenze/jquery.MD5)
[![license agpl](https://img.shields.io/badge/licence-AGPL--3-blue.svg)](http://www.gnu.org/licenses/agpl-3.0.html)
[![Coverage Status](https://coveralls.io/repos/github/zeroincombenze/jquery.MD5/badge.svg?branch=7.0)](https://coveralls.io/github/zeroincombenze/jquery.MD5?branch=7.0)
[![codecov](https://codecov.io/gh/zeroincombenze/jquery.MD5/branch/7.0/graph/badge.svg)](https://codecov.io/gh/zeroincombenze/jquery.MD5/branch/7.0)
[![OCA_project](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-oca-7.svg)](https://github.com/OCA/jquery.MD5/tree/7.0)
[![Tech Doc](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-7.svg)](http://wiki.zeroincombenze.org/en/Odoo/7.0/dev)
[![Help](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-7.svg)](http://wiki.zeroincombenze.org/en/Odoo/7.0/man/)
[![try it](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-7.svg)](http://erp7.zeroincombenze.it)


[![en](http://www.shs-av.com/wp-content/en_US.png)](http://wiki.zeroincombenze.org/it/Odoo/7.0/man)

# jQuery MD5 Plugin

## Usage
Create ([hex](http://en.wikipedia.org/wiki/Hexadecimal)-encoded) [MD5](http://en.wikipedia.org/wiki/MD5) hash of a given string value:
================================================================================================

    var md5 = $.md5('value');

Create ([hex](http://en.wikipedia.org/wiki/Hexadecimal)-encoded) [HMAC](http://en.wikipedia.org/wiki/HMAC)-MD5 hash of a given string value and key:

    var md5 = $.md5('value', 'key');
    
Create raw [MD5](http://en.wikipedia.org/wiki/MD5) hash of a given string value:

    var md5 = $.md5('value', null, true);

Create raw [HMAC](http://en.wikipedia.org/wiki/HMAC)-MD5 hash of a given string value and key:

    var md5 = $.md5('value', 'key', true);

## Requirements
None.

If [jQuery](http://jquery.com/) is not available, the md5 function will be added to the global object:

    var md5 = md5('value');

## License
Released under the [MIT license](http://creativecommons.org/licenses/MIT/).

## Source Code & Download
* Browse and checkout the [source code](https://github.com/blueimp/jQuery-MD5).
* [Download](https://github.com/blueimp/jQuery-MD5/archives/master) the project to add the plugin to your website.

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
