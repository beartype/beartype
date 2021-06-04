#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype callable-based data validation classes** (i.e.,
:mod:`beartype`-specific classes enabling callers to define PEP-compliant data
validators from arbitrary caller-defined callables *not* efficiently generating
stack-free code).

This private submodule defines the core low-level class hierarchy driving the
entire :mod:`beartype` data validation ecosystem.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                              }....................
# All "FIXME:" comments for this submodule reside in this package's "__init__"
# submodule to improve maintainability and readability here.

# ....................{ IMPORTS                           }....................
from abc import ABCMeta
from beartype.roar import BeartypeValeSubscriptionException

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ SUPERCLASSES                      }....................
class _IsABC(object, metaclass=ABCMeta):
    '''
    Abstract base class of all **beartype validator factory subclasses**
    (i.e., subclasses that, when subscripted (indexed) by subclass-specific
    objects, create new :class:`_SubscriptedIs` objects encapsulating those
    objects, themselves suitable for subscripting (indexing)
    :attr:`typing.Annotated` type hints, themselves enforcing subclass-specific
    validation constraints and contracts on :mod:`beartype`-decorated callable
    parameters and returns annotated by those hints).
    '''

    # ..................{ INITIALIZERS                      }..................
    # Ideally, this class method should be typed as returning "NoReturn", but
    # doing so causes MyPy to vociferously complain: e.g.,
    #     beartype/vale/_valeisabc.py:43: error: "__new__" must return a class
    #     instance (got "NoReturn")  [misc]
    def __new__(cls, *args, **kwargs) -> '_IsABC':
        '''
        Prohibit direct instantiation by unconditionally raising an exception.

        Like standard type hints (e.g., :attr:`typing.Union`), this class is
        *only* intended to be subscripted (indexed).

        Raises
        ----------
        BeartypeValeSubscriptionException
            Always.
        '''

        # Murderbot would know what to do here.
        raise BeartypeValeSubscriptionException(
            f'{repr(cls)} not instantiable; '
            f'like most "typing" classes (e.g., "typing.Annotated"), '
            f'this class is only intended to be subscripted (indexed).'
        )
