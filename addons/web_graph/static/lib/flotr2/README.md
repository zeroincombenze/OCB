[![Build Status](https://travis-ci.org/zeroincombenze/flotr2.svg?branch=7.0)](https://travis-ci.org/zeroincombenze/flotr2)
[![license agpl](https://img.shields.io/badge/licence-AGPL--3-blue.svg)](http://www.gnu.org/licenses/agpl-3.0.html)
[![Coverage Status](https://coveralls.io/repos/github/zeroincombenze/flotr2/badge.svg?branch=7.0)](https://coveralls.io/github/zeroincombenze/flotr2?branch=7.0)
[![codecov](https://codecov.io/gh/zeroincombenze/flotr2/branch/7.0/graph/badge.svg)](https://codecov.io/gh/zeroincombenze/flotr2/branch/7.0)
[![OCA_project](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-oca-7.svg)](https://github.com/OCA/flotr2/tree/7.0)
[![Tech Doc](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-7.svg)](http://wiki.zeroincombenze.org/en/Odoo/7.0/dev)
[![Help](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-7.svg)](http://wiki.zeroincombenze.org/en/Odoo/7.0/man/)
[![try it](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-7.svg)](http://erp7.zeroincombenze.it)


[![en](http://www.shs-av.com/wp-content/en_US.png)](http://wiki.zeroincombenze.org/it/Odoo/7.0/man)

Flotr2
======

The Canvas graphing library.

![Google Groups](http://groups.google.com/intl/en/images/logos/groups_logo_sm.gif)

http://groups.google.com/group/flotr2/

Please fork http://jsfiddle.net/cesutherland/ZFBj5/ with your question or bug reproduction case.


API
---

The API consists of a primary draw method which accepts a configuration object, helper methods, and several microlibs.

### Example

```javascript
  var
    // Container div:
    container = document.getElementById("flotr-example-graph"),
    // First data series:
    d1 = [[0, 3], [4, 8], [8, 5], [9, 13]],
    // Second data series:
    d2 = [],
    // A couple flotr configuration options:
    options = {
      xaxis: {
        minorTickFreq: 4
      }, 
      grid: {
        minorVerticalLines: true
      }
    },
    i, graph;

  // Generated second data set:
  for (i = 0; i < 14; i += 0.5) {
    d2.push([i, Math.sin(i)]);
  }

  // Draw the graph:
  graph = Flotr.draw(
    container,  // Container element
    [ d1, d2 ], // Array of data series
    options     // Configuration options
  );
```

### Microlibs

* [underscore.js](http://documentcloud.github.com/underscore/)
* [bean.js](https://github.com/fat/bean)

Extending

Flotr may be extended by adding new plugins and graph types.

### Graph Types

Graph types define how a particular chart is rendered.  Examples include line, bar, pie.

Existing graph types are found in `js/types/`.

### Plugins

Plugins extend the core of flotr with new functionality.  They can add interactions, new decorations, etc.  Examples 
include titles, labels and selection.

The plugins included are found in `js/plugins/`.

Development

This project uses [smoosh](https://github.com/fat/smoosh) to build and [jasmine](http://pivotal.github.com/jasmine/) 
with [js-imagediff](https://github.com/HumbleSoftware/js-imagediff) to test.  Tests may be executed by 
[jasmine-headless-webkit](http://johnbintz.github.com/jasmine-headless-webkit/) with 
`cd spec; jasmine-headless-webkit -j jasmine.yml -c` or by a browser by navigating to 
`flotr2/spec/SpecRunner.html`.

Shoutouts

Thanks to Bas Wenneker, Fabien Ménager and others for all the work on the original Flotr.
Thanks to Jochen Berger and Jordan Santell for their contributions to Flotr2.

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
