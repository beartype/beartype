#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`810`-compliant **lazy import** utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._cave._cavefast import ModuleType
from beartype._data.typing.datatyping import (
    LexicalScope,
    Pep649749Hintable,
)
from beartype._util.module.utilmodget import get_object_module_or_none
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_15
from typing import Optional

# ....................{ CONSTANTS                          }....................
LazyImportType: Optional[type] = None
'''
:pep:`810`-compliant **lazy import type** (i.e., :class:`types.LazyImportType`)
if the active Python interpreter targets Python >= 3.15 *or* :data:`None`
otherwise.
'''

# If the active Python interpreter targets Python >= 3.15, lazy imports exist.
if IS_PYTHON_AT_LEAST_3_15:
    import types
    LazyImportType = getattr(types, 'LazyImportType', None)

# ....................{ CLASSES                            }....................
class Pep810LiveGlobals(dict):
    '''
    **Live global scope** (i.e., dictionary subclass whose own items exclude all
    :pep:`810`-compliant lazily imported attributes of a real global scope but
    whose item lookups defer to that real scope).

    Passed as the global scope of a cloned ``__annotate__()`` dunder method,
    this dictionary induces :mod:`annotationlib` to replace lazily imported
    attributes with unquoted forward reference proxies *without* reifying them.
    Those proxies retain a reference to this dictionary and later evaluate
    against it. Item lookups thus defer to the real global scope (reifying lazy
    imports only when first looked up) rather than a stale snapshot of it.
    '''

    def __init__(self, real_globals: LexicalScope, stripped_globals: LexicalScope):
        super().__init__(stripped_globals)
        self._real_globals = real_globals

    def __contains__(self, name) -> bool:
        return name in self._real_globals or super().__contains__(name)

    def get(self, name, default=None):
        return self[name] if name in self else default

    def __getitem__(self, name):
        real_globals = self._real_globals
        if name in real_globals:
            # Evaluating this name as an expression in the real global scope
            # reifies this attribute if lazily imported. Merely indexing that
            # scope would instead return the unreified lazy import object.
            if isinstance(real_globals[name], LazyImportType):
                return eval(name, real_globals)
            return real_globals[name]
        return super().__getitem__(name)


# ....................{ GETTERS                            }....................
def get_dictable_globals_or_none(
    dictable: Pep649749Hintable) -> Optional[LexicalScope]:
    '''
    **Global scope** (i.e., dictionary mapping from the name to value of each
    globally scoped attribute) accessible to the passed callable, class, or
    module if that object has such a scope *or* :data:`None` otherwise.

    Parameters
    ----------
    dictable : Pep649749Hintable
        Callable, class, or module to be inspected.

    Returns
    -------
    Optional[LexicalScope]
        Either:

        * If this object is a module, the dictionary of this module.
        * If this object is a class, the dictionary of the module declaring this
          class if any.
        * If this object is a callable, the ``__globals__`` dictionary of this
          callable if any.
        * Else, :data:`None`.
    '''

    # If this object is a module, return the dictionary of this module.
    if isinstance(dictable, ModuleType):
        return getattr(dictable, '__dict__', None)
    # Else, this object is *NOT* a module.
    #
    # If this object is a class, return the dictionary of the module declaring
    # this class if any *OR* "None" otherwise.
    elif isinstance(dictable, type):
        dictable_module = get_object_module_or_none(dictable)
        return (
            getattr(dictable_module, '__dict__', None)
            if dictable_module is not None else
            None
        )

    # Else, this object is a callable. Return either this callable's global
    # scope if any *OR* "None" otherwise.
    return getattr(dictable, '__globals__', None)


def reduce_dictable_pep810_lazy_globals_to_pep484_refs(
    dictable: Pep649749Hintable) -> Optional[LexicalScope]:
    '''
    Global scope of the passed callable, class, or module stripped of all
    :pep:`810`-compliant **lazily imported attributes** (i.e., instances of the
    :class:`types.LazyImportType` type) if this scope contains one or more such
    attributes *or* :data:`None` otherwise.

    When passed as the ``globals`` parameter to the standard
    :func:`annotationlib.get_annotations` getter with the ``FORWARDREF`` format,
    this scope forces that getter to replace each lazily imported attribute
    referenced by a type hint with an unquoted forward reference proxy (which
    both :mod:`beartype` and :mod:`annotationlib` already support) rather than
    implicitly reifying that attribute. Doing so preserves the laziness of that
    import, which would otherwise be destroyed merely by introspecting type
    hints at decoration time.

    Parameters
    ----------
    dictable : Pep649749Hintable
        Callable, class, or module to be inspected.

    Returns
    -------
    Optional[LexicalScope]
        Either:

        * If this scope contains one or more lazily imported attributes, a new
          dictionary shallowly copying this scope *without* those attributes.
        * Else, :data:`None`.
    '''

    # If lazy imports are unsupported by this interpreter, return "None".
    if LazyImportType is None:
        return None

    # Global scope of this object if any *OR* "None" otherwise.
    dictable_globals = get_dictable_globals_or_none(dictable)

    # If this object has no global scope, return "None".
    if dictable_globals is None:
        return None
    # Else, this object has a global scope.

    # Note that iterating over a dictionary's values does *NOT* reify lazily
    # imported attributes. Only subsequent name lookups do.
    #
    # If this scope contains *NO* lazily imported attributes, return "None".
    if not any(
        isinstance(global_value, LazyImportType)
        for global_value in dictable_globals.values()
    ):
        return None
    # Else, this scope contains one or more lazily imported attributes.

    # Return a live scope excluding these attributes from its own items.
    return Pep810LiveGlobals(dictable_globals, {
        global_name: global_value
        for global_name, global_value in dictable_globals.items()
        if not isinstance(global_value, LazyImportType)
    })
