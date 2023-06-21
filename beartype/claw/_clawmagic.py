#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **magic** (i.e., global constants widely leveraged throughout
submodules of the :mod:`beartype.claw` subpackage).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from ast import (
    Load,
)
from beartype.meta import (
    NAME,
    VERSION,
)

# ....................{ AST                                }....................
NODE_CONTEXT_LOAD = Load()
'''
**Node context load singleton** (i.e., object suitable for passing as the
``ctx`` keyword parameter accepted by the ``__init__()`` method of various
abstract syntax tree (AST) node classes).
'''

# ....................{ STRINGS                            }....................
BEARTYPE_OPTIMIZATION_MARKER = f'{NAME}{VERSION.replace(".", "v")}'
'''
**Beartype optimization marker** (i.e., placeholder substring suffixing the
``optimization`` parameter passed to the magical hidden
:func:`importlib._bootstrap_external.cache_from_source` function with metadata
unique to the currently installed package name and version of :mod:`beartype`).

This marker uniquifies the filename of bytecode files compiled under beartype
import hooks to the abstract syntax tree (AST) transformation applied by this
version of :mod:`beartype`. Why? Because external callers can trivially enable
and disable that transformation for any module by either calling or not calling
beartype import hooks that accept package name arguments (e.g.,
:func:`beartype.claw.beartype_package`) with the name of a package transitively
containing that module. Compiling a beartyped variant of that module to the same
bytecode file as the non-beartyped variant of that module would erroneously
persist beartyping to that module -- even *after* removing the relevant call to
the :func:`beartype.claw.beartype_package` function! Clearly, that's awful.
Enter @agronholm's phenomenal patch, stage left.

Caveats
----------
**Python requires all optimization markers to be alphanumeric strings.** If this
or *any* other optimization marker contains a non-alphanumeric character, Python
raises a fatal exception resembling:

    ValueError: '-beartype-0.14.2' is not alphanumeric

Ergo, this string globally replaces *all* non-alphanumeric characters that are
otherwise commonly present in the version specifier for this version of
:mod:`beartype` by the arbitrary character ``"v`"" (which is *not* present in
the name of this package and thus suitable as a machine-readable delimiter).
'''

# ....................{ STRINGS ~ cache                    }....................
BEARTYPE_CONF_CACHE_MODULE_NAME = 'beartype.claw._importlib.clawimpcache'
'''
Fully-qualified name of the submodule defining the **hooked module beartype
configuration cache** (i.e., dictionary mapping from the fully-qualified name of
each previously imported submodule of each package previously registered in our
global package trie to the beartype configuration configuring type-checking by
the :func:`beartype.beartype` decorator of that submodule).
'''


BEARTYPE_CONF_CACHE_ATTR_NAME = 'module_name_to_beartype_conf'
'''
Unqualified basename of the hooked module beartype configuration cache relative
to the fully-qualified name of its submodule.
'''

# ....................{ STRINGS ~ decorator                }....................
BEARTYPE_DECORATOR_MODULE_NAME = 'beartype._decor._cache.cachedecor'
'''
Fully-qualified name of the submodule defining the **hooked module beartype
decorator** (i.e., :mod:`beartype` decorator applied by our abstract syntax tree
(AST) node transformer to all applicable callables and classes of third-party
modules).
'''


BEARTYPE_DECORATOR_ATTR_NAME = 'beartype'
'''
Unqualified basename of the hooked module beartype decorator relative
to the fully-qualified name of its submodule.
'''
