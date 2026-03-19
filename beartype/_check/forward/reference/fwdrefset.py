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
from beartype._check.forward.reference.fwdreftyping import (
    TupleBeartypeForwardRefs)

# ....................{ TESTERS                            }....................
#FIXME: Unit test us up, please. *sigh*
def set_beartype_ref_proxies_exception_prefix(
    ref_proxies: TupleBeartypeForwardRefs, exception_prefix: str) -> None:
    '''
    Overwrite the default value of the ``__exception_prefix_beartype__`` class
    variables bound to all passed :mod:`beartype`-specific **forward reference
    proxies** (i.e., classes whose :class:`.BeartypeForwardRefMeta` metaclass
    defers the resolution of forward reference type hints referencing type
    hints that have yet to be defined in the lexical scope of external callers)
    with the passed exception prefix.

    Parameters
    ----------
    ref_proxies : TupleBeartypeForwardRefs
        Tuple of zero or more forward reference proxies to overwrite the
        the ``__exception_prefix_beartype__`` class variables of.
    exception_prefix : str
        Human-readable substring prefixing exception messages to be raised by
        these proxies.
    '''
    assert isinstance(ref_proxies, tuple), f'{repr(ref_proxies)} not tuple.'
    assert isinstance(exception_prefix, str), (
        f'{repr(exception_prefix)} not string.')

    # Avoid circular import dependencies.
    from beartype._check.forward.reference.fwdreftest import (
        die_unless_beartype_ref_proxy)

    #FIXME: [SPEED] Optimize into a "while" loop. *lol*
    # For each such beartype-specific forward reference proxy, set the exception
    # prefix associated with this proxy to... this exception prefix. So cool!
    for ref_proxy in ref_proxies:
        # If this item is *NOT* actually such a proxy, raise an exception.
        die_unless_beartype_ref_proxy(ref_proxy)
        # Else, this item is actually such a proxy.

        # Overwrite this proxy's default prefix with the passed prefix.
        ref_proxy.__exception_prefix_beartype__ = exception_prefix
