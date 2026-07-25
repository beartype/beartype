#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype import hook magic** (i.e., global constants widely leveraged
throughout submodules of the :mod:`beartype.claw` subpackage).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
# Note that attempting to import the equivalent global constants from the
# "beartype.meta" submodule is known to unsafely induce infinite recursion
# during "importlib" machinery handling performed by the
# beartype.claw._importlib._clawimpfileloader.BeartypeSourceFileLoader.get_code()
# method. Therefore, rather than importing:
# * The unsafe "beartype.meta.NAME" global constant here, we instead manually
#   embed the literal substring "beartype" into global constants defined below.
# * The unsafe "beartype.meta.VERSION" global constant here, we instead import
#   the safe "beartype._metaverse.VERSION" global constant known *NOT* to induce
#   such recursion.
from beartype._metaverse import VERSION

# ....................{ STRINGS                            }....................
OPTIMIZATION_MARKER_BEARTYPE = f'beartype{VERSION.replace(".", "v")}'
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
-------
**Python requires all optimization markers to be alphanumeric strings.** If this
or *any* other optimization marker contains a non-alphanumeric character, Python
raises a fatal exception resembling:

    ValueError: '-beartype-0.14.2' is not alphanumeric

Ergo, this string globally replaces *all* non-alphanumeric characters that are
otherwise commonly present in the version specifier for this version of
:mod:`beartype` by the arbitrary character ``"v`"" (which is *not* present in
the name of this package and thus suitable as a machine-readable delimiter).
'''

# ....................{ STRINGS ~ names                    }....................
BEARTYPE_DECORATOR_FUNC_NAME = '__beartype__'
'''
Unqualified basename of the beartype decorator as imported into the current
user-defined module being imported and thus transformed by the
:class:`beartype.claw._ast.clawastmain.BeartypeNodeTransformer` subclass.
'''


BEARTYPE_RAISER_FUNC_NAME = '__die_if_unbearable_beartype__'
'''
Unqualified basename of the beartype exception-raiser as imported into the
current user-defined module being imported and thus transformed by the
:class:`beartype.claw._ast.clawastmain.BeartypeNodeTransformer` subclass.
'''

# ....................{ STRINGS ~ names : claw             }....................
BEARTYPE_CLAW_SMOKE_TEST_SUBMODULE_NAME = (
    'beartype.claw._importlib._clawimpsmoke')
'''
Fully-qualified name of the **beartype import hook activation smoke test**
(i.e., private empty submodule isolated to the :mod:`beartype` codebase
facilitating a crude smoke test, enabling :mod:`beartype.claw` import hooks to
efficiently detect whether they were successfully activated or not).
'''

# ....................{ STRINGS ~ names : claw : state     }....................
BEARTYPE_CLAW_STATE_OBJ_NAME = '__claw_state_beartype__'
'''
Unqualified basename of the beartype import hook state as imported into the
current user-defined module being imported and thus transformed by the
:class:`beartype.claw._ast.clawastmain.BeartypeNodeTransformer` subclass.
'''


BEARTYPE_CLAW_STATE_CONF_CACHE_VAR_NAME = 'module_name_to_beartype_conf'
'''
Unqualified basename of the **hooked module beartype configuration cache**
(i.e., dictionary mapping from the fully-qualified name of each previously
imported submodule of each package previously registered in our global package
trie to the beartype configuration configuring type-checking by the
:func:`beartype.beartype` decorator of that submodule) relative to the
beartype import hook state, which contains this cache.
'''

# ....................{ STRINGS ~ names : pep : 302        }....................
# Note that this hook was manually constructed from each "name: {value}" line
# printed by the following code snippet in a Python script:
#     from beartype._util.utilobjget import get_object_name
#     for meta_path_hook_index, meta_path_hook in enumerate(meta_path):
#         print(f'meta_path_hook {meta_path_hook_index}: {repr(meta_path_hook)}')
#         print(f'\tname: {get_object_name(obj=meta_path_hook, is_fallback_type_name=True)}')
#         print(f'\tqualname: {getattr(meta_path_hook, "__qualname__", "")}')
#         print(f'\ttype: {type(meta_path_hook)}')
#         print(f'\tdir: {dir(meta_path_hook)}')
STANDARD_META_PATH_ITEM_NAMES = frozenset((
    # ....................{ STANDARD                       }....................
    # Python predefines three standard meta path hooks for importing (in order)
    # builtin modules, frozen modules, and pathed modules (i.e., modules
    # residing on either the global "sys.path" list *OR* package-specific
    # "__path__" dunder attribute). See also this official documentation:
    #     https://docs.python.org/3/reference/import.html#finders-and-loaders

    # Python's standard builtin module importer.
    '_frozen_importlib.BuiltinImporter',

    # Python's standard frozen module importer.
    '_frozen_importlib.FrozenImporter',

    # Python's standard pathed module importer.
    '_frozen_importlib_external.PathFinder',

    # ....................{ NON-STANDARD                   }....................
    # Third-party "distutils"-specific meta path hook. Since this hook is
    # non-standard, the fully-qualified name of this hook *SHOULD* be
    # unsuitable as an item of this purportedly "standard" set. However:
    # * "setuptools" requires "distutils", which unconditionally installs this
    #   hook at interpreter startup.
    # * "setuptools" is one of only two official Python package management
    #   tools. The other, of course, is Hatch.
    # * Almost all real-world Python app stacks require "setuptools" as a
    #   transitive (if not explicit) dependency.
    # * Omitting the fully-qualified name of this hook here would then cause our
    #   "beartype.claw" import hook activity detector (also known as
    #   Leycec's Polychromatic Hook Elicitor, just because) to include this name
    #   in exception output. Problematically, that exception output advises end
    #   users to contact the authors of all listed meta path hooks and beg them
    #   to add support for "sys.path_hooks"-based import hooks (thus including
    #   "beartype.claw" import hooks). Manual inspection of "distutils"-specific
    #   meta path hook, however, trivially shows that this hook is sufficiently
    #   simplistic that it *CANNOT* be the cause of "beartype.claw" import hook
    #   inactivity. Including this name here not only sanitizes exception output
    #   but also reduces confusion (and thus negativity) directed towards
    #   beartype later. We'll take it. We've got to take it! Pain is a choice.
    #   See also this upstream kludge in the "distutils" codebase:
    #       https://github.com/pypa/setuptools/blob/main/_distutils_hack/__init__.py
    '_distutils_hack.DistutilsMetaFinder',
))
'''
Frozen set of the **fully-qualified names** (i.e., ``.``-delimited unambiguously
identifying strings) of all :pep:`302`-compliant **standard meta path hooks**
(i.e., items of the global :obj:`sys.meta_path` list predefined by the active
Python interpreter at interpreter startup *before* any third-party package or
module subsequently modifies that list).

Equivalently, this is the frozen set of all strings iteratively returned by the
``get_object_name(obj=meta_path_hook, is_fallback_type_name=True)`` getter when
passed each such meta path hook.
'''


# Note that this hook was manually constructed from each "name: {value}" line
# printed by the following code snippet in a Python script:
#     from beartype._util.utilobjget import get_object_name
#     for path_hook_index, path_hook in enumerate(path_hooks):
#         print(f'path_hook {path_hook_index}: {repr(path_hook)}')
#         print(f'\tname: {get_object_name(obj=path_hook, is_fallback_type_name=True)}')
#         print(f'\tqualname: {path_hook.__qualname__}')
#         print(f'\ttype: {type(path_hook)}')
#         print(f'\tdir: {dir(path_hook)}')
STANDARD_PATH_HOOKS_ITEM_NAMES = frozenset((
    # ....................{ STANDARD                       }....................
    # Python predefines two standard path hooks for importing (in order):
    # * Zipped modules, intentionally included below.
    # * Pathed modules (i.e., modules residing on either the global "sys.path"
    #   list *OR* package-specific "__path__" dunder attribute), intentionally
    #   omitted below. Why? Because the fully-qualified name of this standard
    #   path hook is non-trivial and possibly dynamic across disparate Python
    #   environments. Callers are encouraged to instead call the lower-level
    #   _get_standard_file_finder_path_hook_basename_scoped() to safely obtain
    #   the lexically scoped name of this standard path hook.

    # Python's standard zipped module importer.
    'zipimport.zipimporter',
))
'''
Frozen set of the **fully-qualified names** (i.e., ``.``-delimited unambiguously
identifying strings) of all :pep:`302`-compliant **standard path hooks**
(i.e., items of the global :obj:`sys.path_hooks` list predefined by the active
Python interpreter at interpreter startup *before* any third-party package or
module subsequently modifies that list).

Equivalently, this is the frozen set of all strings iteratively returned by the
``get_object_name(obj=path_hook, is_fallback_type_name=True)`` getter when
passed each such path hook.
'''

# ....................{ STRINGS ~ names : pep : 695        }....................
BEARTYPE_HINT_PEP695_FORWARDREF_ITER_FUNC_NAME = (
    '__iter_hint_pep695_forwardref_beartype__')
'''
Unqualified basename of the :pep:`695`-compliant **type alias unqualified
relative forward reference iterator** (i.e., generator iteratively creating and
yielding one forward reference proxy for each unqualified relative forward
reference in the passed :pep:`695`-compliant type alias as imported into the
current user-defined module being imported and thus transformed by the
:class:`beartype.claw._ast.clawastmain.BeartypeNodeTransformer` subclass.
'''
