#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype cave-specific abstract base classes (ABCs).**

This submodule declares non-standard ABCs subclassed by  implementing .
'''

# ....................{ IMPORTS                           }....................
from abc import ABCMeta, abstractmethod

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ FUNCTIONS                         }....................
def _check_methods(C: type, *methods: str) -> (bool, type(NotImplemented)):
    '''
    Private utility function called by abstract base classes (ABCs)
    implementing structural subtyping by detecting whether the passed class or
    some superclass of that class defines all of the methods with the passed
    method names.

    For safety, this function has been duplicated as is from its eponymous
    counterpart in the private stdlib :mod:`_colletions_abc` module.

    Parameters
    ----------
    C : type
        Class to be validated as defining these methods.
    methods : Tuple[str]
        Tuple of the names of all methods to validate this class as defining.

    Returns
    ----------
    ``True``
        Only if this class defines all of these methods.
    ``NotImplemented``
        Only if this class fails to define one or more of these methods.
    '''

    mro = C.__mro__
    for method in methods:
        for B in mro:
            if method in B.__dict__:
                if B.__dict__[method] is None:
                    return NotImplemented
                break
        else:
            return NotImplemented

    return True

# ....................{ TYPES ~ scalar                    }....................
# This class is documented in the "beartype.cave" for readability.
class _BoolType(metaclass=ABCMeta):
    '''
    Type of all **booleans** (i.e., objects defining the ``__bool__()`` dunder
    method; objects reducible in boolean contexts like ``if`` conditionals to
    either ``True`` or ``False``).

    This abstract base class (ABC) has been implemented ala standard container
    ABCs in the private stdlib :mod:`_collections_abc` module (e.g., the
    trivial :mod:`_collections_abc.Sized` type).

    See Also
    ----------
    :class:`beartype.cave.BoolType`
        Full documentation for this ad-hoc :mod:`beartype`-specific type.
    '''

    __slots__ = ()

    @abstractmethod
    def __bool__(self):
        return False

    @classmethod
    def __subclasshook__(cls, C):
        if cls is _BoolType:
            return _check_methods(C, '__bool__')
        return NotImplemented
