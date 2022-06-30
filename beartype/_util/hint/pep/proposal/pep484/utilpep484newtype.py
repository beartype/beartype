#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-compliant **new type hint utilities** (i.e.,
callables generically applicable to :pep:`484`-compliant types).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep484Exception
from beartype.typing import Any
from beartype._data.hint.pep.sign.datapepsigns import HintSignNewType
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_10
from types import FunctionType

# ....................{ TESTERS                            }....................
# If the active Python interpreter targets Python >= 3.10 and thus defines
# "typing.NewType" type hints as instances of that class, implement this tester
# unique to prior Python versions to raise an exception.
if IS_PYTHON_AT_LEAST_3_10:
    def is_hint_pep484_newtype_pre_python310(hint: object) -> bool:
        raise BeartypeDecorHintPep484Exception(
            'is_hint_pep484_newtype_pre_python310() assumes Python < 3.10, '
            'but current Python interpreter targets Python >= 3.10.'
        )
# Else, the active Python interpreter targets Python < 3.10 and thus defines
# "typing.NewType" type hints as closures returned by that function. Since
# these closures are sufficiently dissimilar from all other type hints to
# require unique detection, implement this tester unique to this obsolete
# Python version to detect these closures.
else:
    def is_hint_pep484_newtype_pre_python310(hint: object) -> bool:

        # Return true only if...
        return (
            # This hint is a pure-Python function *AND*...
            #
            # Note that we intentionally do *NOT* call the callable() builtin
            # here, as that builtin erroneously returns false positives for
            # non-standard classes defining the __call__() dunder method to
            # unconditionally raise exceptions. Critically, this includes most
            # PEP 484-compliant type hints, which naturally fail to define both
            # the "__module__" *AND* "__qualname__" dunder instance variables
            # accessed below. Shoot me now, fam.
            isinstance(hint, FunctionType) and
            # This callable is a closure created and returned by the
            # typing.NewType() function. Note that:
            #
            # * The "__module__" and "__qualname__" dunder instance variables
            #   are *NOT* generally defined for arbitrary objects but are
            #   specifically defined for callables.
            # * "__qualname__" is safely available under Python >= 3.3.
            # * This test derives from the observation that the concatenation
            #   of this callable's "__qualname__" and "__module" dunder
            #   instance variables suffices to produce a string unambiguously
            #   identifying whether this hint is a "NewType"-generated closure:
            #       >>> from typing import NewType
            #       >>> UserId = t.NewType('UserId', int)
            #       >>> UserId.__qualname__
            #       >>> 'NewType.<locals>.new_type'
            #       >>> UserId.__module__
            #       >>> 'typing'
            f'{hint.__module__}.{hint.__qualname__}'.startswith(
                'typing.NewType.')
        )


is_hint_pep484_newtype_pre_python310.__doc__ = '''
    ``True`` only if the passed object is a Python < 3.10-specific
    :pep:`484`-compliant **new type** (i.e., closure created and returned by
    the :func:`typing.NewType` closure factory function).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Caveats
    ----------
    **New type aliases are a complete farce and thus best avoided.**
    Specifically, these PEP-compliant type hints are *not* actually types but
    rather **identity closures** that return their passed parameters as is.
    Instead, where distinct types are:

    * *Not* required, simply annotate parameters and return values with the
      desired superclasses.
    * Required, simply:

      * Subclass the desired superclasses as usual.
      * Annotate parameters and return values with those subclasses.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a Python < 3.10-specific
        :pep:`484`-compliant new type.
    '''

# ....................{ GETTERS                            }....................
def get_hint_pep484_newtype_class(hint: Any) -> type:
    '''
    User-defined class aliased by the passed :pep:`484`-compliant **new type**
    (i.e., object created and returned by the :func:`typing.NewType` type hint
    factory).

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    type
        User-defined class aliased by this :pep:`484`-compliant new type.

    Raises
    ----------
    BeartypeDecorHintPep484Exception
        If this object is *not* a :pep:`484`-compliant new type.

    See Also
    ----------
    :func:`is_hint_pep484_newtype`
        Further commentary.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_sign

    # If this object is *NOT* a PEP 484-compliant "NewType" hint, raise an
    # exception.
    if get_hint_pep_sign(hint) is not HintSignNewType:
        raise BeartypeDecorHintPep484Exception(
            f'Type hint {repr(hint)} not "typing.NewType".')
    # Else, this object is a PEP 484-compliant "NewType" hint.

    # Return the unqualified classname referred to by this reference. Note
    # that this requires violating privacy encapsulation by accessing a dunder
    # instance variable unique to closures created by the typing.NewType()
    # closure factory function.
    return hint.__supertype__
