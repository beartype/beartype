#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
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
from beartype._check.forward.reference.fwdrefmeta import BeartypeForwardRefMeta

# ....................{ TESTERS                            }....................
#FIXME: Unit test us up, please.
def is_forwardref(obj: object) -> bool:
    '''
    :data:`True` only if the passed object is a **forward reference subclass**
    (i.e., class whose metaclass is class:`.BeartypeForwardRefMeta`).

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
