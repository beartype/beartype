#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype code-based object data validation classes** (i.e.,
:mod:`beartype`-specific classes enabling callers to define PEP-compliant data
validators from arbitrary caller-defined objects tested via explicitly
supported object introspectors efficiently generating stack-free code).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                              }....................
# All "FIXME:" comments for this submodule reside in this package's "__init__"
# submodule to improve maintainability and readability here.

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeValeSubscriptionException
from beartype.vale._valeisabc import _IsABC
from beartype.vale._valeissub import _SubscriptedIs
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.func.utilfuncscope import (
    CallableScope,
    add_func_scope_attr,
)
from typing import Any

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CLASSES ~ subscriptable           }....................
#FIXME: Unit test us up.
class IsAttr(_IsABC):
    '''
    **Beartype object attribute validator factory** (i.e., class that, when
    subscripted (indexed) by both the name of any object attribute *and* any
    :class:`_SubscriptedIs` object created by subscripting any
    :mod:`beartype.vale` class for validating that attribute, creates another
    :class:`_SubscriptedIs` object suitable for subscripting (indexing)
    :attr:`typing.Annotated` type hints, which validates that
    :mod:`beartype`-decorated callable parameters and returns annotated by
    those hints define an attribute with that name satisfying that attribute
    validator).

    This class efficiently validates that callable parameters and returns
    define arbitrary object attributes satisfying arbitrary validators
    subscripting (indexing) this class. Any :mod:`beartype`-decorated callable
    parameter or return annotated by a :attr:`typing.Annotated` type hint
    subscripted (indexed) by this class subscripted (indexed) by any object
    attribute name and validator (e.g., ``typing.Annotated[{cls},
    beartype.vale.IsAttr[{attr_name}, {attr_vale}]]`` for any class ``{cls}``,
    object attribute name ``{attr_name}`, and object attribute validator
    ``{attr_value}``) validates that parameter or return value to be an
    instance of that class defining an attribute with that name satisfying that
    attribute validator.

    **This class incurs no time performance penalties at call time.** Whereas
    the general-purpose :class:`beartype.vale.Is` class necessarily calls the
    caller-defined callable subscripting that class at call time and thus
    incurs a minor time performance penalty, this class efficiently reduces to
    one-line tests in :mod:`beartype`-generated wrapper functions *without*
    calling any callables and thus incurs *no* time performance penalties.

    Examples
    ----------
    .. _code-block:: python

       # Import the requisite machinery.
       >>> import numpy as np
       >>> from beartype import beartype
       >>> from beartype.vale import IsAttr, IsEqual
       >>> from typing import Annotated

       # Validator matching only the NumPy dtype for 64-bit floats.
       >>> IsDtypeFloat64 = IsEqual[dtype(np.float64)]

       # Type hint matching only two-dimensional NumPy arrays of 64-bit floats.
       >>> Numpy2DArrayOfFloats = typing.Annotated[ndarray,
       ...     IsAttr['dtype', IsDtypeFloat64], IsAttr['ndim', IsEqual[2]]]

       # Type hint matching only one-dimensional NumPy arrays of 64-bit floats.
       >>> Numpy1DArrayOfFloats = typing.Annotated[ndarray,
       ...     IsAttr['dtype', IsDtypeFloat64], IsAttr['ndim', IsEqual[1]]]

       # NumPy arrays of well-known real number series.
       >>> FAREY_2D_ARRAY_OF_FLOATS = np.array(
       ...     [[0/1, 1/8,], [1/7, 1/6,], [1/5, 1/4], [2/7, 1/3], [3/8, 2/5]])
       >>> FAREY_1D_ARRAY_OF_FLOATS = np.array(
       ...     [3/7, 1/2, 4/7, 3/5, 5/8, 2/3, 5/7, 3/4, 4/5, 5/6, 6/7, 7/8])

       # Annotate callables by those type hints.
       >>> @beartype
       ... def sum_2d(array: Numpy2DArrayOfFloats) -> Numpy1DArrayOfFloats:
       ...     """
       ...     One-dimensional NumPy array of 64-bit floats produced by summing
       ...     passed two-dimensional NumPy array of 64-bit floats along its
       ...     second dimension.
       ...     """
       ...     return array.sum(axis=1)

       #FIXME: Resume here tomorrow, please.
       # Call those callables with parameters satisfying those hints.
       >>> sum_2d(FAREY_2D_ARRAY_OF_FLOATS)
       ????????????????????????????????????

       # Call those callables with parameters not satisfying those hints.
       >>> sum_2d(FAREY_1D_ARRAY_OF_FLOATS)

    See Also
    ----------
    :class:`beartype.vale.Is`
        Further commentary.

    .. _PEP 560:
       https://www.python.org/dev/peps/pep-0560
    '''

    # ..................{ DUNDERS                           }..................
    #FIXME: Implement us up, please.
    #FIXME: Unit test memoization, please.
    @callable_cached
    def __class_getitem__(
        cls, attr_name: str, attr_validator: _SubscriptedIs) -> _SubscriptedIs:
        '''
        `PEP 560`_-compliant dunder method creating and returning a new
        :class:`_SubscriptedIs` object validating object attributes with the
        passed name satisfying the passed validator, suitable for subscripting
        `PEP 593`_-compliant :attr:`typing.Annotated` type hints.

        This method is memoized for efficiency.

        Parameters
        ----------
        attr_name : str
            Arbitrary attribute name to validate that parameters and returns
            define in a manner satisfying the passed validator.
        attr_validator : _SubscriptedIs
            Attribute validator to validate that attributes with the passed
            name of parameters and returns satisfy.

        Returns
        ----------
        _SubscriptedIs
            New object encapsulating this validation.

        Raises
        ----------
        BeartypeValeSubscriptionException
            If this class was subscripted by either:

            * *No* arguments.
            * One argument.
            * Three or more arguments.

        See Also
        ----------
        :class:`IsAttr`
            Usage instructions.

        .. _PEP 560:
           https://www.python.org/dev/peps/pep-0560
        .. _PEP 593:
           https://www.python.org/dev/peps/pep-0593
        '''

        # If...
        if (
            # This class was subscripted by either no arguments *OR* two or
            # more arguments *AND*...
            isinstance(obj, tuple) and
            # This class was subscripted by no arguments...
            not obj
        # Then raise an exception.
        ):
            raise BeartypeValeSubscriptionException(
                f'{repr(cls)} subscripted by empty tuple.')
        # Else, this class was subscripted by one or more arguments. In any
        # case, accept this object as is. See the class docstring for details.
        # print(f'IsEqual[{repr(obj)}]')

        # Callable inefficiently validating against this object.
        is_valid = lambda pith: pith == obj

        # Dictionary mapping from the name to value of each local attribute
        # referenced in the "is_valid_code" snippet defined below.
        is_valid_code_locals: CallableScope = {}

        # Name of a new parameter added to the signature of wrapper functions
        # whose value is this object, enabling this object to be tested in
        # those functions *WITHOUT* additional stack frames.
        obj_name = add_func_scope_attr(
            attr=obj, attr_scope=is_valid_code_locals)

        # Code snippet efficiently validating against this object.
        is_valid_code=f'{{obj}} == {obj_name}'

        # Create and return this subscription.
        return _SubscriptedIs(
            is_valid=is_valid,
            is_valid_code=is_valid_code,
            is_valid_code_locals=is_valid_code_locals,
            get_repr=lambda: f'{cls.__name__}[{repr(obj)}]',
        )
