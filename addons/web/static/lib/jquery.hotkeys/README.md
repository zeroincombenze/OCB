[![Build Status](https://travis-ci.org/zeroincombenze/jquery.hotkeys.svg?branch=10.0)](https://travis-ci.org/zeroincombenze/jquery.hotkeys)
[![license agpl](https://img.shields.io/badge/licence-AGPL--3-blue.svg)](http://www.gnu.org/licenses/agpl-3.0.html)
[![Coverage Status](https://coveralls.io/repos/github/zeroincombenze/jquery.hotkeys/badge.svg?branch=10.0)](https://coveralls.io/github/zeroincombenze/jquery.hotkeys?branch=10.0)
[![codecov](https://codecov.io/gh/zeroincombenze/jquery.hotkeys/branch/10.0/graph/badge.svg)](https://codecov.io/gh/zeroincombenze/jquery.hotkeys/branch/10.0)
[![OCA_project](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-oca-10.svg)](https://github.com/OCA/jquery.hotkeys/tree/10.0)
[![Tech Doc](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-10.svg)](http://wiki.zeroincombenze.org/en/Odoo/10.0/dev)
[![Help](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-10.svg)](http://wiki.zeroincombenze.org/en/Odoo/10.0/man/)
[![try it](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-10.svg)](http://erp10.zeroincombenze.it)


[![en](http://www.shs-av.com/wp-content/en_US.png)](http://wiki.zeroincombenze.org/it/Odoo/7.0/man)

#About
**jQuery Hotkeys** is a plug-in that lets you easily add and remove handlers for keyboard events anywhere in your code supporting almost any key combination.  

This plugin is based off of the plugin by Tzury Bar Yochay: [jQuery.hotkeys](http://github.com/tzuryby/hotkeys)
================================================================================================

The syntax is as follows:

    $(expression).bind(types, keys, handler);
    $(expression).unbind(types, handler);
    
    $(document).bind('keydown', 'ctrl+a', fn);
    
    // e.g. replace '$' sign with 'EUR'
    $('input.foo').bind('keyup', '$', function(){
      this.value = this.value.replace('$', 'EUR');
    });

## Types
Supported types are `'keydown'`, `'keyup'` and `'keypress'`

## Notes

If you want to use more than one modifiers (e.g. alt+ctrl+z) you should define them by an alphabetical order e.g. alt+ctrl+shift

Hotkeys aren't tracked if you're inside of an input element (unless you explicitly bind the hotkey directly to the input). This helps to avoid conflict with normal user typing.

## jQuery Compatibility

Works with jQuery 1.4.2 and newer.

It known to be working with all the major browsers on all available platforms (Win/Mac/Linux)

 * IE 6/7/8
 * FF 1.5/2/3
 * Opera-9
 * Safari-3
 * Chrome-0.2

### Addendum

Firefox is the most liberal one in the manner of letting you capture all short-cuts even those that are built-in in the browser such as `Ctrl-t` for new tab, or `Ctrl-a` for selecting all text. You can always bubble them up to the browser by returning `true` in your handler.

Others, (IE) either let you handle built-in short-cuts, but will add their functionality after your code has executed. Or (Opera/Safari) will *not* pass those events to the DOM at all.

*So, if you bind `Ctrl-Q` or `Alt-F4` and your Safari/Opera window is closed don't be surprised.*

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
