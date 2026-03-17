#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **forward reference testers** (i.e.,  low-level callables testing
various properties of forward reference proxy subclasses deferring the
resolution of a stringified type hint referencing an attribute that has yet to
be defined and annotating a class or callable decorated by the
:func:`beartype.beartype` decorator).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.forward.reference.fwdreftyping import BeartypeForwardRef
from beartype._check.forward.reference._fwdrefmeta import BeartypeForwardRefMeta
from beartype._data.typing.datatypingport import TypeIs

# ....................{ TESTERS                            }....................
def is_beartype_ref_proxy(obj: object) -> TypeIs[BeartypeForwardRef]:
    '''
    :data:`True` only if the passed object is a :mod:`beartype`-specific
    **forward reference proxy** (i.e., class whose
    :class:`.BeartypeForwardRefMeta` metaclass defers the resolution of a
    forward reference type hint referencing a type hint that has yet to be
    defined in the lexical scope of an external caller).

    Caveats
    -------
    **This high-level tester should always be called in lieu of lower-level
    operations,** especially attempts to detect forward reference proxies by
    calling either the :func:`isinstance` or :func:`issubclass` builtins. Since
    forward reference proxies proxy calls to those builtins, forward reference
    proxies *cannot* be detected by calling either of those builtins.

    Parameters
    ----------
    obj : object
        Object to be tested.

    Returns
    -------
    bool
        :data:`True` only if this object is a forward reference subclass.
    '''

    # Return true only if the class of this object is the metaclass of all
    # forward reference subclasses, implying this object to be such a subclass.
    return obj.__class__ is BeartypeForwardRefMeta
