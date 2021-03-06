#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype code-based operator validation classes** (i.e.,
:mod:`beartype`-specific classes enabling callers to define PEP-compliant
validators from arbitrary caller-defined objects tested via explicitly
supported operators efficiently generating stack-free code).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                              }....................
# All "FIXME:" comments for this submodule reside in this package's "__init__"
# submodule to improve maintainability and readability here.

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeValeSubscriptionException
from beartype.vale._valeisabc import _IsABC
from beartype._vale._valesub import _SubscriptedIs
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.func.utilfuncscope import (
    CallableScope,
    add_func_scope_attr,
)
from typing import Any

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CLASSES ~ subscriptable           }....................
#FIXME: Generalize to support arbitrary binary operators by:
#* Define a new "_IsOperatorBinaryABC(_IsABC, metaclass=ABCMeta)" superclass.
#* In that superclass:
#  * Define a stock __class_getitem__() method whose implementation is
#    sufficiently generic so as to be applicable to all subclasses. To do so,
#    this method should access class variables defined by those subclasses.
#  * Note that there is absolutely no reason or point to define abstract class
#    methods forcing subclasses to define various metadata, for the unfortunate
#    reason that abstract class methods do *NOT* actually enforce subclasses
#    that aren't instantiable anyway to implement those methods. *sigh*
#* Refactor "IsEqual" to:
#  * Subclass that superclass.
#  * Define the following class variables, which the superclass
#    __class_getitem__() method will internally access to implement itself:
#    from operator import __eq__
#
#    class IsEqual(_IsOperatorBinaryABC):
#        _operator = __eq__
#        _operator_code = '=='
#
#Ridiculously sweet, eh? We know.

class IsEqual(_IsABC):
    '''
    **Beartype object equality validator factory** (i.e., class that, when
    subscripted (indexed) by any object, creates a new :class:`_SubscriptedIs`
    object suitable for subscripting (indexing) :attr:`typing.Annotated` type
    hints, validating that :mod:`beartype`-decorated callable parameters and
    returns annotated by those hints are equal to that object).

    This class efficiently validates that callable parameters and returns are
    equal to the arbitrary object subscripting (indexing) this class. Any
    :mod:`beartype`-decorated callable parameter or return annotated by a
    :attr:`typing.Annotated` type hint subscripted (indexed) by this class
    subscripted (indexed) by any object (e.g., ``typing.Annotated[{cls},
    beartype.vale.IsEqual[{obj}]]`` for any class ``{cls}``  and object
    ``{obj}`) validates that parameter or return value to equal that object
    under the standard ``==`` equality comparison.

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
    .. code-block:: python

       # Import the requisite machinery.
       >>> from beartype import beartype
       >>> from beartype.vale import IsEqual
       >>> from typing import Annotated

       # Lists of the first ten items of well-known simple whole number series.
       >>> WHOLE_NUMBERS      = [0, 1, 2, 3, 4,  5,  6,  7,  8,  9]
       >>> WHOLE_NUMBERS_EVEN = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
       >>> WHOLE_NUMBERS_ODD  = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]

       # Type hint matching only lists of integers equal to one of these lists.
       >>> SimpleWholeNumberSeries = Annotated[
       ...     list[int],
       ...     IsEqual[WHOLE_NUMBERS] |
       ...     IsEqual[WHOLE_NUMBERS_EVEN] |
       ...     IsEqual[WHOLE_NUMBERS_ODD]
       ... ]

       # Annotate callables by those type hints.
       >>> @beartype
       ... def guess_next(series: SimpleWholeNumberSeries) -> int:
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

       # Call those callables with parameters unequal to one of those objects.
       >>> guess_next([1, 2, 3, 6, 7, 14, 21, 42,])
       beartype.roar._roarexc.BeartypeCallHintPepParamException: @beartyped
       guess_next() parameter series=[1, 2, 3, 6, 7, 14, 21, 42] violates type
       hint typing.Annotated[list[int], IsEqual[[0, 1, 2, 3, 4, 5, 6, 7, 8,
       9]] | IsEqual[[0, 2, 4, 6, 8, 10, 12, 14, 16, 18]] | IsEqual[[1, 3, 5,
       7, 9, 11, 13, 15, 17, 19]]], as value [1, 2, 3, 6, 7, 14, 21, 42]
       violates data constraint IsEqual[[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]] |
       IsEqual[[0, 2, 4, 6, 8, 10, 12, 14, 16, 18]] | IsEqual[[1, 3, 5, 7, 9,
       11, 13, 15, 17, 19]].

    See Also
    ----------
    :class:`beartype.vale.Is`
        Further commentary.

    .. _PEP 560:
       https://www.python.org/dev/peps/pep-0560
    '''

    # ..................{ DUNDERS                           }..................
    @callable_cached
    def __class_getitem__(cls, obj: Any) -> _SubscriptedIs:
        '''
        `PEP 560`_-compliant dunder method creating and returning a new
        :class:`_SubscriptedIs` object validating equality against the passed
        arbitrary object suitable for subscripting `PEP 593`_-compliant
        :attr:`typing.Annotated` type hints.

        This method is memoized for efficiency.

        Parameters
        ----------
        obj : Any
            Arbitrary object to validate parameters and returns against.

        Returns
        ----------
        _SubscriptedIs
            New object encapsulating this validation.

        Raises
        ----------
        BeartypeValeSubscriptionException
            If this class was subscripted by *no* arguments.

        See Also
        ----------
        :class:`IsEqual`
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
