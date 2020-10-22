#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype** `PEP 544`_**-compliant type hint utilities.**

This private submodule is *not* intended for importation by downstream callers.

.. _PEP 544:
    https://www.python.org/dev/peps/pep-0544
'''

# ....................{ TODO                              }....................
#FIXME: Add support for user-defined multiple-inherited protocols (i.e.,
#user-defined classes directly subclassing the "typing.Protocol" ABC and one or
#more other superclasses). Note that these protocols are literally user-defined
#generics (i.e., they subclass "typing.Generic") and thus require as a
#prerequisite that we first implement support for user-defined generics.

# ....................{ IMPORTS                           }....................
from beartype._util.py.utilpyversion import (
    IS_PYTHON_AT_LEAST_3_8,
)

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ TESTERS                           }....................
# If the active Python interpreter targets at least Python >= 3.8 and thus
# supports PEP 544 and the "typing.Protocol" superclass, define this tester to
# conditionally test the passed object.
if IS_PYTHON_AT_LEAST_3_8:
    from typing import Generic, Protocol


    _PEP544_PROTOCOL_PURE_MRO = (Protocol, Generic, object)
    '''
    Tuple of the latter three classes in the method resolution order (MRO) of
    *all* `PEP 544`_**-compliant user-defined pure protocols** (i.e.,
    user-defined subclasses both decorated by the
    :attr:`typing.runtime_checkable` decorator and subclassing *only* the
    :attr:`typing.Protocol` abstract base class).

    The first class in the MRO of any class is that class itself and thus
    ignorable for most intents, including this.

    Examples
    ----------
        >>> import typing
        >>> class ProtocolCustom(t.Protocol): pass
        >>> ProtocolCustom.__mro__
        (<class 'ProtocolCustom'>, <class 'typing.Protocol'>, <class 'typing.Generic'>, <class 'object'>)
        >>> ProtocolCustom.__mro__[1:] == _PEP544_PROTOCOL_PURE_MRO
        True
    '''


    def is_hint_pep544_protocol_pure(hint: object) -> bool:

        # Return true only if...
        return (
            # This hint is a class *AND*...
            isinstance(hint, type) and
            # This class subclasses the "typing.Protocol" superclass *AND*...
            issubclass(hint, Protocol) and
            # The method resolution order (MRO) for this class contains exactly
            # four classes, the first of which is this class itself and thus
            # ignorable and the latter three of which exactly match the
            # "_PEP544_PROTOCOL_PURE_MRO" global.
            hint.__mro__[1:] == _PEP544_PROTOCOL_PURE_MRO
        )
# Else, the active Python interpreter does *NOT* target at least Python >= 3.8
# and thus does *NOT* support PEP 544 and the "typing.Protocol" superclass. In
# this case, define this tester to unconditionally return false.
else:
    def is_hint_pep544_protocol_pure(hint: object) -> bool:
        return False


# Document this tester.
is_hint_pep544_protocol_pure.__doc__ = '''
    ``True`` only if the passed object is a `PEP 544`_**-compliant user-defined
    pure protocol** (i.e., user-defined subclass both decorated by the
    :attr:`typing.runtime_checkable` decorator and subclassing *only* the
    :attr:`typing.Protocol` abstract base class).

    This tester is provided to enable the :func:`beartype.beartype` decorator
    to optimize the common case of user-defined pure protocols, which trivially
    reduce to calls to the builtin :func:`isinstance` function.

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a `PEP 544`_-compliant user-defined
        pure protocol.

    .. _PEP 544:
       https://www.python.org/dev/peps/pep-0544
    '''
