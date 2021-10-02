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
from typing import TYPE_CHECKING, Any

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ METACLASSES                       }....................
class _IsMeta(ABCMeta):
    '''
    Metaclass all **beartype validator factory subclasses** (i.e.,
    :class:`_IsABC` subclasses).
    '''

    # ..................{ INITIALIZERS                      }..................
    def __init__(cls, classname, superclasses, attr_name_to_value) -> None:
        super().__init__(classname, superclasses, attr_name_to_value)

        # Sanitize the fully-qualified name of the module declaring this class
        # from the private name of the module implementing this classes to the
        # public name of the module exporting this class, improving end user
        # clarity and usability.
        cls.__module__ = 'beartype.vale'

    # ..................{ DUNDERS                           }..................
    #FIXME: Report an upstream mypy issue. It's deeply unfortunate that mypy
    #fails to support the __class_getitem__() dunder method first introduced
    #with PEP 560. The kludge below is simply that; it's a kludge, which we
    #wouldn't have to do if mypy properly supported PEP 560.
    #FIXME: Ah-hah! This is awful. Instead, what we want to do is extend
    #support for beartype validators back to Python 3.7 (especially) and 3.6
    #(urgh!) by:
    #* Refactoring the "_IsABC" superclass to implement __getitem__() rather
    #  than __class_getitem__().
    #* Privatizing all subclasses of that superclass: e.g.,
    #  * Rename "IsAttr" to "_IsAttrClass".
    #* Instantiating all of those subclasses with single line singletons in
    #  "__init__": e.g.,
    #    IsAttr = _IsAttrClass()
    #    IsEqual = _IsEqualClass()
    #    ...
    #Voila! Pretty sweetness, eh? Yup. Yup, it is.

    # If beartype is currently being subjected to static type checking by a
    # static type checker that is almost certainly mypy, prevent that checker
    # from erroneously emitting one error for each otherwise valid
    # subscription of each "_IsABC" subclass: e.g.,
    #     $ mypy
    #     error: The type "Type[IsAttr]" is not generic and not indexable  [misc]
    if TYPE_CHECKING:
        def __getitem__(self, *args, **kwargs) -> Any:
            raise BeartypeValeSubscriptionException(
                f'{repr(self)} not indexable.')

# ....................{ SUPERCLASSES                      }....................
class _IsABC(object, metaclass=_IsMeta):
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
    #     beartype.vale._factory._valeisabc.py:43: error: "__new__" must return a class
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

    # # ..................{ DUNDERS                           }..................
    # def __getitem__(self, *args, **kwargs) -> Any:
    #     '''
    #     Prohibit direct instantiation by unconditionally raising an exception.
    #
    #     Like standard type hints (e.g., :attr:`typing.Union`), this class is
    #     *only* intended to be subscripted (indexed).
    #
    #     Raises
    #     ----------
    #     BeartypeValeSubscriptionException
    #         Always.
    #     '''
    #
    #     # Murderbot would know what to do here.
    #     raise BeartypeValeSubscriptionException(
    #         f'{repr(self)} not instantiable; '
    #         f'like most "typing" classes (e.g., "typing.Annotated"), '
    #         f'this class is only intended to be subscripted (indexed).'
    #     )
