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
from beartype.roar import (
    BeartypeValeSubscriptionException,
)
from beartype.vale import Is
from beartype.vale._valeissub import (
    SubscriptedIs,
    SubscriptedIsValidator,
)
from beartype._decor._code._pep._pepmagic import OPERATOR_SUFFIX_LEN_OR
from beartype._util.func.utilfuncscope import (
    CallableScope,
    add_func_scope_attr,
)
# from beartype._util.text.utiltextrepr import (
#     represent_object,
# )
from typing import Any

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CLASSES ~ subscriptable           }....................
#FIXME: Unit test us up.
class IsEqual(Is):
    '''
    **Beartype** ``==`` **validator factory.**

    This class efficiently validates that callable parameters and returns are
    equal to (i.e., ``==``) at least one of the one or more arbitrary objects
    subscripting (indexing) this class. Any :mod:`beartype`-decorated callable
    parameter or return annotated by a :attr:`typing.Annotated` type hint
    subscripted (indexed) by this class subscripted (indexed) by any arbitrary
    object (e.g., of the form ``typing.Annotated[{cls},
    beartype.vale.IsEqual[{obj}]]`` for any class ``{cls}``  and object
    ``{obj}`) validates that that parameter or return value is equal to at
    least one of those objects according to the standard ``==`` operator.

    When subscripted by two or more objects, this class is shorthand for
    independently subscripting this class by each of those objects conjoined by
    the ``|`` set operator. These two type hints are semantically equivalent:

    * ``Annotated[str, IsEqual['No talking.', 'No smoking.']]``.
    * ``Annotated[str, IsEqual['No talking.'] | IsEqual['No smoking.']]``.

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
       ...     IsEqual[WHOLE_NUMBERS_EVEN, WHOLE_NUMBERS_ODD]
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
    '''

    # ..................{ DUNDERS                           }..................
    def __class_getitem__(cls, args: Any) -> SubscriptedIs:
        '''
        `PEP 560`_-compliant dunder method dynamically generating a new
        :class:`SubscriptedIs` object validating equality against the passed
        arbitrary object suitable for subscripting `PEP 593`_-compliant
        :attr:`typing.Annotated` type hints.

        See the class docstring for usage instructions.

        Parameters
        ----------
        args : Any
            If this class was subscripted by either:

            * No arbitrary objects, the empty tuple.
            * One arbitrary object, that object as is.
            * Two or more arbitrary objects, the tuple of those objects.

        Returns
        ----------
        SubscriptedIs
            New object encapsulating this equality test.

        Raises
        ----------
        BeartypeValeSubscriptionException
            If this class was subscripted by *no* arguments.

        .. _PEP 560:
           https://www.python.org/dev/peps/pep-0560
        .. _PEP 593:
           https://www.python.org/dev/peps/pep-0593
        '''

        # Callable inefficiently testing equality against these objects.
        is_valid: SubscriptedIsValidator = None  # type: ignore[assignment]

        # Code snippet efficiently testing equality against these objects.
        is_valid_code = ''

        # Dictionary mapping from the name to value of each local attribute
        # referenced in the "is_valid_code" snippet defined below.
        is_valid_code_locals: CallableScope = {}

        # If this class was subscripted by either no or two or more objects...
        if isinstance(args, tuple):
            # If this class was subscripted by no objects, raise an exception.
            if not args:
                raise BeartypeValeSubscriptionException(
                    '{repr(cls)} subscripted by empty tuple.')
            # Else, this class was subscripted by two or more objects.

            # Callable inefficiently testing equality against these objects.
            is_valid = lambda obj: any(
                obj == args_item for args_item in args)

            # For each object subscripting this class...
            for args_item in args:
                # Name of a new parameter added to the signature of wrapper
                # functions whose value is this object, enabling this object to
                # be tested for directly in the body of those functions
                # *WITHOUT* imposing additional stack frames.
                args_item_name = add_func_scope_attr(
                    attr=args_item, attr_scope=is_valid_code_locals)

                # Append an expression testing equality against this object to
                # this code.
                is_valid_code += f'{{obj}} == {args_item_name} or '

            # Strip the erroneous " or" suffix appended by the last subscripted
            # object from this code.
            is_valid_code = is_valid_code[:-OPERATOR_SUFFIX_LEN_OR]
        # Else, this class was subscripted by one object. In this case...
        else:
            # Callable inefficiently testing equality against this object.
            is_valid = lambda obj: obj == args

            # Name of a new parameter added to the signature of wrapper
            # functions whose value is this object, enabling this object to be
            # tested for directly in the body of those functions *WITHOUT*
            # imposing additional stack frames.
            args_name = add_func_scope_attr(
                attr=args, attr_scope=is_valid_code_locals)

            # Code snippet efficiently testing equality against this object.
            is_valid_code=f'{{obj}} == {args_name}'

        # Create and return this subscription.
        return SubscriptedIs(
            is_valid=is_valid,
            is_valid_code=is_valid_code,
            is_valid_code_locals=is_valid_code_locals,
            get_repr=lambda: f'{cls.__name__}[{represent_args(args)}]',
        )


#FIXME: Shift elsewhere, please.
#FIXME: Unit test us up.
#FIXME: Docstring us up.
def represent_args(args: Any) -> str:

    # If these arguments are tuple, the caller was passed either no arguments
    # or two or more arguments. In either case...
    if isinstance(args, tuple):
        # If the caller was passed two or more arguments...
        if args:
            # Machine-readable representation of these arguments.
            args_repr = repr(args)

            # Return this representation stripped of:
            # * The "(" character prefixing this tuple.
            # * The ")" character suffixing this tuple.
            return args_repr[1:-1]
        # Else, the caller was passed *NO* arguments. In this case, return the
        # empty string.
        else:
            return ''
    # Else, the caller was passed exactly one argument. In this case, return
    # the machine-readable representation of that argument as is.
    else:
        return repr(args)
