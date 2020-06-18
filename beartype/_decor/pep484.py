#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator** `PEP 484`_ **support.**

This private submodule implements `PEP 484`_ (i.e., Type Hints) support.
Specifically, this submodule transparently converts high-level special-purpose
abstract types and methods defined by the stdlib :mod:`typing` module into
low-level general-use concrete types and code snippets independent of that
module.

This private submodule is *not* intended for importation by downstream callers.

.. _PEP 484:
   https://www.python.org/dev/peps/pep-0484
'''

# ....................{ IMPORTS                           }....................
from beartype.cave import (
    AnyType,
    StrType,
)

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ GETTERS                           }....................
def get_func_signature(func_name: str) -> Signature:
    '''
    :class:`Signature` instance encapsulating the passed callable's signature.

    If `PEP 563`_ is conditionally active for this callable, this function
    additionally resolves all postponed annotations on this callable to their
    referents (i.e., the intended annotations to which those postponed
    annotations refer).

    Parameters
    ----------
    func : CallableTypes
        Non-class callable to parse the signature of.
    func_name : str
        Human-readable name of this callable.

    Returns
    ----------
    Signature
        :class:`Signature` instance encapsulating this callable's signature,
        dynamically parsed by the :mod:`inspect` module from this callable.

    Raises
    ----------
    BeartypeDecorPep563Exception
        If evaluating a postponed annotation on this callable raises an
        exception (e.g., due to that annotation referring to local state no
        longer accessible from this deferred evaluation).

    .. _PEP 563:
       https://www.python.org/dev/peps/pep-0563
    '''
    assert isinstance(func_name, str), '{!r} not a string.'.format(func_name)
