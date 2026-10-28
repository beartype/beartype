#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **forward reference setters** (i.e.,  low-level callables setting
various properties on forward reference proxy subclasses deferring the
resolution of a stringified type hint referencing an attribute that has yet to
be defined and annotating a class or callable decorated by the
:func:`beartype.beartype` decorator).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.cls.call.calldataabc import BeartypeCallDataABC
from beartype._check.forward.reference.fwdreftyping import (
    TupleBeartypeForwardRefs)

# ....................{ SETTERS                            }....................
#FIXME: Unit test us up, please. *sigh*
def set_beartype_ref_proxies_classvars_uninitted(
    ref_proxies: TupleBeartypeForwardRefs,
    call_curr: BeartypeCallDataABC,
    exception_prefix: str,
) -> None:
    '''
    Overwrite the default values of all **uninitialized class variables** (i.e.,
    class variables that the
    :func:`beartype._check.forward.reference.fwdrefproxy._proxy_hint_ref`
    function assigned default uninitialized values rather than non-default
    initialized values) bound to all passed :mod:`beartype`-specific **forward
    reference proxies** (i.e., classes whose
    :class:`.BeartypeForwardRefMetaclass` metaclass defers the resolution of
    forward reference type hints referencing type hints that have yet to be
    defined in the lexical scope of external callers) with the passed
    corresponding parameters.

    This setter is intended to be called late during dynamic type-checking code
    generation, typically due to the passed parameters being unavailable earlier
    when these forward reference proxies were first instantiated.

    This setter specifically overwrites on these forward reference proxies the
    default uninitialized values of:

    * The ``__call_curr_beartype__`` class variable with the passed beartype
      call metadata, enabling proxies whose forward references reference yet
      other forward references to reliably proxy the latter as well.
    * The ``__exception_prefix_beartype__`` class variable with the passed
      exception prefix, improving the readability of exceptions raised at
      type-checking wrapper call time when one of these proxies fails to resolve
      the reference it proxies. Constructing this prefix is typically
      computationally expensive and thus deferred as late as possible [read:
      *NOW*].

    Parameters
    ----------
    ref_proxies : TupleBeartypeForwardRefs
        Tuple of zero or more forward reference proxies to overwrite the
        the ``__exception_prefix_beartype__`` class variables of.
    call_curr : BeartypeCallDataABC
        **Beartype call metadata** (i.e., dataclass aggregating *all* common
        metadata encapsulating the user-defined callable, type, or statement
        currently being type-checked by the end user).
    exception_prefix : str
        Human-readable substring prefixing exception messages to be raised by
        these proxies.
    '''
    assert isinstance(ref_proxies, tuple), f'{repr(ref_proxies)} not tuple.'
    assert isinstance(call_curr, BeartypeCallDataABC), (
        f'{repr(call_curr)} not beartype call metadata.')
    assert isinstance(exception_prefix, str), (
        f'{repr(exception_prefix)} not string.')

    # Avoid circular import dependencies.
    from beartype._check.forward.reference.fwdreftest import (
        die_unless_beartype_ref_proxy)

    # Replace the passed non-minified beartype call metadata with the equivalent
    # minified beartype call metadata.
    #
    # Note that this is *not* simply a negligible optimization reducing space
    # consumption, although it certainly is that. Minification has the
    # beneficial side effect of effectively shallowly copying this metadata in
    # the common case that this metadata is an instance of the non-minified
    # "BeartypeCallDecorFuncData" dataclass. For efficiency, that instance is
    # reused across *EVERY* call to the @beartype decorator, preventing these
    # proxies from referencing that instance across @beartype decorations. These
    # proxies thus instead references the shallow copy of that instance produced
    # by minifying that instance. Phew! It doesn't have to make sense. It's QA.
    call_curr = call_curr.minify()

    #FIXME: [SPEED] Optimize into a "while" loop. *lol*
    # For each passed forward reference proxy...
    for ref_proxy in ref_proxies:
        # If this item is *NOT* actually such a proxy, raise an exception.
        die_unless_beartype_ref_proxy(ref_proxy)
        # Else, this item is actually such a proxy.

        # Overwrite all uninitialized class variables bound to this proxy with
        # the corresponding passed parameters.
        ref_proxy.__call_curr_beartype__ = call_curr
        ref_proxy.__exception_prefix_beartype__ = exception_prefix
