#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype code-based operator data validation classes** (i.e.,
:mod:`beartype`-specific classes enabling callers to define PEP-compliant data
validators from arbitrary caller-defined objects tested via explicitly
supported operators efficiently generating stack-free code).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                              }....................
# All "FIXME:" comments for this submodule reside in this package's "__init__"
# submodule to improve maintainability and readability here.

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeValeSubscriptionException
from beartype.vale._valeis import Is
from beartype.vale._valeissub import SubscriptedIs
from beartype._util.func.utilfuncscope import (
    CallableScope,
    add_func_scope_attr,
)
from typing import Any

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CLASSES ~ subscriptable           }....................
#FIXME: Unit test us up.
class IsEqual(Is):
    '''
    **Beartype** ``==`` **validator factory.**

    This class efficiently validates that callable parameters and returns are
    equal to (i.e., ``==``) exactly the arbitrary object subscripting
    (indexing) this class. Any :mod:`beartype`-decorated callable parameter or
    return annotated by a :attr:`typing.Annotated` type hint subscripted
    (indexed) by this class subscripted (indexed) by any arbitrary object
    (e.g., ``typing.Annotated[{cls}, beartype.vale.IsEqual[{obj}]]`` for any
    class ``{cls}``  and object ``{obj}`) validates that parameter or return
    value equals that object via a standard ``==``-based comparison.

    This class is a generalization of the `PEP 586`_-compliant
    :attr:`typing.Literal` type hint, because this class does everything
    :attr:`typing.Literal` does and substantially more. Superficially,
    :attr:`typing.Literal` also validates that callable parameters and returns
    are equal to (i.e., ``==``) the literal object subscripting (indexing) that
    :attr:`typing.Literal` type hint. The similarity ends there, however.
    :attr:`typing.Literal` is only subscriptable by literal :class:`bool`,
    :class:`bytes`, :class:`int`, :class:`str`, :class:`Enum`, and
    ``type(None)`` objects; this class is subscriptable by *any* object.

    **This class incurs no time performance penalties at call time.** Whereas
    the general-purpose :class:`beartype.vale.Is` class necessarily calls the
    caller-defined callable subscripting that class at call time and thus
    incurs a minor time performance penalty, this class efficiently reduces to
    one-line tests in :mod:`beartype`-generated wrapper functions *without*
    calling any callables and thus incurs *no* time performance penalties.

    Caveats
    ----------
    **This class is intentionally subscriptable by only a single object.** Why?
    Disambiguity. When subscripted by variadic positional (i.e., one or more)
    objects, this class internally treats those objects as items of a tuple to
    validate equality against rather than as independent objects to iteratively
    validate equality against. Since this is non-intuitive, callers should
    avoid subscripting this class by multiple objects. Although non-intuitive,
    this is also unavoidable. The ``__class_getitem__`` dunder method obeys
    the same semantics as the ``__getitem__`` dunder method, which is unable to
    differentiate between being subscripted two or more objects and being
    subscripted by a tuple of two or more objects. Since being able to validate
    equality against tuples of two or more objects is essential and since this
    class being subscripted by two or more objects would trivially reduce to
    shorthand for the existing ``|`` set operator already supported by this
    class, this class preserves support for tuples of two or more objects at a
    cost of non-intuitive results when subscripted by multiple objects.

    Don't blame us. We didn't vote for `PEP 560`_.

    Examples
    ----------
    .. _code-block:: python

       # Import the requisite machinery.
       >>> from beartype import beartype
       >>> from beartype.vale import IsEqual
       >>> from typing import Annotated

       # Lists of the first ten items of well-known whole number series.
       >>> WHOLE_NUMBERS      = [0, 1, 2, 3, 4,  5,  6,  7,  8,  9]
       >>> WHOLE_NUMBERS_EVEN = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
       >>> WHOLE_NUMBERS_ODD  = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]

       # Annotate callables by "typing.Annotated" subscripted with
       # "beartype.vale.IsEqual" subscripted with any object.
       >>> @beartype
       ... def guess_next(series: Annotated[list[int],
       ...     IsEqual[WHOLE_NUMBERS] |
       ...     IsEqual[WHOLE_NUMBERS_EVEN] |
       ...     IsEqual[WHOLE_NUMBERS_ODD]
       ... ) -> int:
       ...     """
       ...     Guess the next whole number in the passed whole number series.
       ...     """
       ...     if series == WHOLE_NUMBERS: return WHOLE_NUMBERS[-1] + 1
       ...     else:                       return        series[-1] + 2

       # Call those callables with parameters equal to one of those objects.
       >>> guess_next(list(range(10)))
       10
       >>> guess_next([number*2 for number in range(10)])
       20

    See Also
    ----------
    :class:`beartype.vale.Is`
        Further details.

    .. _PEP 560:
       https://www.python.org/dev/peps/pep-0560
    '''

    # ..................{ DUNDERS                           }..................
    def __class_getitem__(cls, obj: Any) -> SubscriptedIs:
        '''
        `PEP 560`_-compliant dunder method dynamically generating a new
        :class:`SubscriptedIs` object validating equality against the passed
        arbitrary object suitable for subscripting `PEP 593`_-compliant
        :attr:`typing.Annotated` type hints.

        See the class docstring for usage instructions.

        Parameters
        ----------
        obj : Any
            Arbitrary object to validate parameters and returns against.

        Returns
        ----------
        SubscriptedIs
            New object encapsulating this validation.

        Raises
        ----------
        BeartypeValeSubscriptionException
            If this class was subscripted by *no* arguments.

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
                '{repr(cls)} subscripted by empty tuple.')
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
        return SubscriptedIs(
            is_valid=is_valid,
            is_valid_code=is_valid_code,
            is_valid_code_locals=is_valid_code_locals,
            get_repr=lambda: f'{cls.__name__}[{repr(obj)}]',
        )
