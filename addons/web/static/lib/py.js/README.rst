[![Build Status](https://travis-ci.org/zeroincombenze/py.js.svg?branch=10.0)](https://travis-ci.org/zeroincombenze/py.js)
[![license agpl](https://img.shields.io/badge/licence-AGPL--3-blue.svg)](http://www.gnu.org/licenses/agpl-3.0.html)
[![Coverage Status](https://coveralls.io/repos/github/zeroincombenze/py.js/badge.svg?branch=10.0)](https://coveralls.io/github/zeroincombenze/py.js?branch=10.0)
[![codecov](https://codecov.io/gh/zeroincombenze/py.js/branch/10.0/graph/badge.svg)](https://codecov.io/gh/zeroincombenze/py.js/branch/10.0)
[![OCA_project](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-oca-10.svg)](https://github.com/OCA/py.js/tree/10.0)
[![Tech Doc](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-docs-10.svg)](http://wiki.zeroincombenze.org/en/Odoo/10.0/dev)
[![Help](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-help-10.svg)](http://wiki.zeroincombenze.org/en/Odoo/10.0/man/)
[![try it](http://www.zeroincombenze.it/wp-content/uploads/ci-ct/prd/button-try-it-10.svg)](http://erp10.zeroincombenze.it)


[![en](http://www.shs-av.com/wp-content/en_US.png)](http://wiki.zeroincombenze.org/it/Odoo/7.0/man)

What
====
====



Syntax

* Lambdas and ternaries should be parsed but are not implemented (in
  the evaluator)
* Only floats are implemented, ``int`` literals are parsed as floats.
* Octal and hexadecimal literals are not implemented
* Srings are backed by JavaScript strings and probably behave like
  ``unicode`` more than like ``str``
* Slices don't work

Builtins

``py.js`` currently implements the following builtins:

``type``
    Restricted to creating new types, can't be used to get an object's
    type (yet)

``None``

``True``

``False``

``NotImplemented``
    Returned from rich comparison methods when the comparison is not
    implemented for this combination of operands. In ``py.js``, this
    is also the default implementation for all rich comparison methods.

``issubclass``

``object``

``bool``
    Does not inherit from ``int``, since ``int`` is not currently
    implemented.

``float``

``str``

``tuple``
    Constructor/coercer is not implemented, only handles literals

``list``
    Same as tuple (``list`` is currently an alias for ``tuple``)

``dict``
    Implements trivial getting, setting and len, nothing beyond that.

Note that most methods are probably missing from all of these.

Data model protocols

``py.js`` currently implements the following protocols (or
sub-protocols) of the `Python 2.7 data model
<>`_:

Rich comparisons
    Pretty much complete (including operator fallbacks), although the
    behavior is currently undefined if an operation does not return
    either a ``py.bool`` or ``NotImplemented``.

    ``__hash__`` is supported (and used), but it should return **a
    javascript string**. ``py.js``'s dict build on javascript objects,
    reimplementing numeral hashing is worthless complexity at this
    point.

Boolean conversion
    Implementing ``__nonzero__`` should work.

Customizing attribute access
    Protocols for getting and setting attributes (including new-style
    extension) fully implemented but for ``__delattr__`` (since
    ``del`` is a statement)

Descriptor protocol
    As with attributes, ``__delete__`` is not implemented.

Callable objects
    Work, although the handling of arguments isn't exactly nailed
    down. For now, callables get two (javascript) arguments ``args``
    and ``kwargs``, holding (respectively) positional and keyword
    arguments.

    Conflicts are *not* handled at this point.

Collections Abstract Base Classes
    Container is the only implemented ABC protocol (ABCs themselves
    are not currently implemented) (well technically Callable and
    Hashable are kind-of implemented as well)

Numeric type emulation
    Operators are implemented (but not tested), ``abs``, ``divmod``
    and ``pow`` builtins are not implemented yet. Neither are ``oct``
    and ``hex`` but I'm not sure we care (I'm not sure we care about
    ``pow`` or even ``divmod`` either, for that matter)

Utilities

``py.js`` also provides (and exposes) a few utilities for "userland"
implementation:

``def``
    Wraps a native javascript function into a ``py.js`` function, so
    that it can be called from native expressions.

    Does not ensure the return types are type-compatible with
    ``py.js`` types.

    When accessing instance methods, ``py.js`` automatically wraps
    these in a variant of ``py.def``, to behave as Python's (bound)
    methods.

Why
===

Originally, to learn about Pratt parsers (which are very, very good at
parsing expressions with lots of infix or mixfix symbols). The
evaluator part came because "why not" and because I work on a product
with the "feature" of transmitting Python expressions (over the wire)
which the client is supposed to evaluate.

How
===

At this point, only three steps exist in ``py.js``: tokenizing,
parsing and evaluation. It is possible that a compilation step be
added later (for performance reasons).

To evaluate a Python expression, the caller merely needs to call
`py.eval`_. `py.eval`_ takes a mandatory Python
expression to evaluate (as a string) and an optional context, for the
substitution of the free variables in the expression::

    > py.eval("type in ('a', 'b', 'c') and foo", {type: 'c', foo: true});
    true

This is great for one-shot evaluation of expressions. If the
expression will need to be repeatedly evaluated with the same
parameters, the various parsing and evaluation steps can be performed
separately: `py.eval`_ is really a shortcut for sequentially calling
`py.tokenize`_, `py.parse`_ and `py.evaluate`_.

API
===

.. _py.eval:

``py.eval(expr[, context])``
    "Do everything" function, to use for one-shot evaluation of a
    Python expression: it will internally handle the tokenizing,
    parsing and actual evaluation of the Python expression without
    having to perform these separately.

    ``expr``
        Python expression to evaluate
    ``context``
        context dictionary holding the substitutions for the free
        variables in the expression

.. _py.tokenize:

``py.tokenize(expr)``
    ``expr``
        Python expression to tokenize

.. _py.parse:

``py.parse(tokens)``
    Parses a token stream and returns an abstract syntax tree of the
    expression (if the token stream represents a valid Python
    expression).

    A parse tree is stateless and can be memoized and used multiple
    times in separate evaluations.

    ``tokens``
         stream of tokens returned by `py.tokenize`_

.. _py.evaluate:

``py.evaluate(ast[, context])``
    ``ast``
        The output of `py.parse`_
    ``context``
        The evaluation context for the Python expression.

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
