#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype core data validation classes.**

This private submodule defines the core low-level class hierarchy driving the
entire :mod:`beartype` data validation ecosystem.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                              }....................
# All "FIXME:" comments for this submodule reside in this package's "__init__"
# submodule to improve maintainability and readability here.

# ....................{ IMPORTS                           }....................
from beartype.roar import (
    BeartypeValeSubscriptionException,
    BeartypeValeLambdaWarning,
)
from beartype.vale._valeissub import (
    SubscriptedIs,
    SubscriptedIsValidator,
)
from beartype._util.func.utilfuncscope import (
    CallableScope,
    add_func_scope_attr,
)
from beartype._util.text.utiltextrepr import (
    represent_object,
    represent_func,
)

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ CLASSES ~ subscriptable           }....................
class Is(object):
    '''
    **Beartype data validator factory** (i.e., class that, when subscripted
    (indexed) by a caller-defined data validation function returning ``True``
    when an arbitrary object passed to that function satisfies an arbitrary
    constraint, creates a new :class:`SubscriptedIs` object encapsulating that
    function suitable for subscripting (indexing) :attr:`typing.Annotated` type
    hints, which then enforce that validation on :mod:`beartype`-decorated
    callable parameters and returns annotated by those hints).

    Subscripting (indexing) this class produces an :class:`SubscriptedIs`
    object that validates the internal integrity, consistency, and structure of
    arbitrary objects ranging from simple builtin scalars like integers and
    strings to complex data structures defined by third-party packages like
    NumPy arrays and Pandas DataFrames. For portability, :class:`SubscriptedIs`
    objects are:

    * **PEP-compliant** and thus guaranteed to *never* violate existing or
      future standards.
    * **Safely ignorable** by *all* static and runtime type checkers other than
      :mod:`beartype` itself.

    Usage
    ----------
    Callers are expected to (in order):

    #. Annotate a callable parameter or return to be validated with a `PEP
       593`_-compliant :attr:`typing.Annotated` type hint.
    #. Subscript that hint with (in order):

       #. The type expected by that parameter or return.
       #. One or more subscriptions (indexations) of this class, each itself
          subscripted (indexed) by a **data validator** (i.e., function
          accepting a single arbitrary object and returning either ``True`` if
          that object satisfies an arbitrary constraint *or* ``False``
          otherwise). If that hint is subscripted by:

          * Only one subscription of this class, that parameter or return
            satisfies that hint when both:

            * That parameter or return is an instance of the expected type.
            * That data validator returns ``True`` when passed that parameter
              or return.

          * Two or more subscriptions of this class, that parameter or return
            satisfies that hint when both:

            * That parameter or return is an instance of the expected type.
            * *All* data validators subscripting *all* subscriptions of this
              class return ``True`` when passed that parameter or return.

          Formally, the signature of each data validator *must* resemble:

          .. _code-block:: python

             def is_object_valid(obj) -> bool:
                 return bool(obj)

          Equivalently, each validator *must* satisfy the type hint
          ``collections.abc.Callable[[typing.Any,], bool]``. If not the case,
          an exception is raised. Note that:

          * If that parameter or return is *not* an instance of the expected
            type, **no validator is called.** Equivalently, each validator is
            called *only* when that parameter or return is already an instance
            of the expected type. Validators need *not* revalidate that type
            (e.g., by passing that parameter or return and type to the
            :func:`isinstance` builtin).
          * The name of each validator is irrelevant. For convenience, most
            validators are defined as nameless lambda functions.

    For example, the following type hint only accepts non-empty strings:

    .. _code-block:: python

       Annotated[str, Is[lambda text: bool(text)]]

    :class:`SubscriptedIs` objects also support an expressive domain-specific
    language (DSL) enabling callers to trivially synthesize new objects from
    existing objects with standard Pythonic math operators:

    * **Negation** (i.e., ``not``). Negating an :class:`SubscriptedIs` object
      with the ``~`` operator synthesizes a new :class:`SubscriptedIs` object
      whose data validator returns ``True`` only when the data validator of the
      original object returns ``False``. For example, the following type hint
      only accepts strings containing *no* periods:

      .. _code-block:: python

         Annotated[str, ~Is[lambda text: '.' in text]]

    * **Conjunction** (i.e., ``and``). Conjunctively combining two or more
      :class:`SubscriptedIs` objects with the ``&`` operator synthesizes a new
      :class:`SubscriptedIs` object whose data validator returns ``True`` only
      when all data validators of the original objects return ``True``. For
      example, the following type hint only accepts non-empty strings
      containing *no* periods:

      .. _code-block:: python

         Annotated[str, (
              Is[lambda text: bool(text)] &
             ~Is[lambda text: '.' in text]
         )]

    * **Disjunction** (i.e., ``or``). Disjunctively combining two or more
      subscriptions with the ``|`` operator returns ``True`` only when at least
      one subscription returns ``True``. For example, this type hint accepts
      both empty strings *and* non-empty strings containing at least one
      period:
    * **Disjunction** (i.e., ``or``). Disjunctively combining two or more
      :class:`SubscriptedIs` objects with the ``|`` operator synthesizes a new
      :class:`SubscriptedIs` object whose data validator returns ``True`` only
      when at least one data validator of the original objects returns
      ``True``. For example, the following type hint accepts both empty strings
      *and* non-empty strings containing at least one period:

      .. _code-block:: python

         Annotated[str, (
             ~Is[lambda text: bool(text)] |
              Is[lambda text: '.' in text]
         )]

    See also the **Examples** subsection below.

    Caveats
    ----------
    **This class is currently only supported by the** :func:`beartype.beartype`
    **decorator.** All other static and runtime type checkers silently ignore
    subscriptions of this class subscripting :attr:`typing.Annotated` type
    hints.

    **This class incurs a minor time complexity cost at call time.**
    Specifically, each type hint of a :mod:`beartype`-decorated callable
    subscripted by a subscription of this class adds one additional stack frame
    to each call of that callable. While negligible (in the average case), this
    cost can become non-negligible when compounded across multiple type hints
    annotating a frequently called :mod:`beartype`-decorated callable --
    especially when those type hints are subscripted by multiple subscriptions
    of this class at different nesting levels.

    **This class prohibits instantiation.** This class is *only* intended to be
    subscripted. Attempting to instantiate this class into an object will raise
    an :exc:`BeartypeValeSubscriptionException` exception.

    Examples
    ----------
    .. _code-block:: python

       from beartype import beartype
       from beartype.vale import Is
       from typing import Annotated

       IsUnquoted = Is[lambda text: '"' not in text and "'" not in text]
       """
       Constraint matching only unquoted strings.
       """

       UnquotedString = Annotated[str, IsUnquoted]
       """
       Type hint matching only unquoted strings.
       """

       @beartype
       def quote_text(text: UnquotedString) -> str:
           """
           Double-quote the passed unquoted string.
           """

           return f'"{text}"'

       IsLengthy = Is[lambda text: 4 <= len(text) <= 14]
       """
       Constraint matching only strings with lengths ranging ``[4, 14]``
       (inclusive).
       """

       UnquotedLengthyString = Annotated[str, IsUnquoted, IsLengthy]
       """
       Type hint matching only unquoted strings with lengths ranging ``[4,
       14]`` (inclusive).
       """

       @beartype
       def snip_text(text: UnquotedLengthyString) -> UnquotedString:
           """
           Return the prefix spanning characters ``[0, 3]`` (inclusive) of the
           passed unquoted string with a length ranging ``[4, 14]``
           (inclusive).
           """

           # "This is guaranteed to work," says beartype.
           return text[:3]

    .. _PEP 593:
       https://www.python.org/dev/peps/pep-0593
    '''

    # ..................{ INITIALIZERS                      }..................
    def __new__(cls, *args, **kwargs):
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
            f'Class "{cls.__name__}" not instantiable; '
            f'index this class with data validation functions instead '
            f'(e.g., "{cls.__name__}[lambda obj: bool(obj)]").'
        )

    # ..................{ DUNDERS                           }..................
    def __class_getitem__(
        cls, is_valid: SubscriptedIsValidator) -> SubscriptedIs:
        '''
        `PEP 560`_-compliant dunder method dynamically generating a new
        :class:`SubscriptedIs` object from the passed data validation function
        suitable for subscripting `PEP 593`_-compliant :attr:`typing.Annotated`
        type hints.

        See the class docstring for usage instructions.

        Parameters
        ----------
        is_valid : Callable[[Any,], bool]
            **Data validator** (i.e., caller-defined function accepting a
            single arbitrary object and returning either ``True`` if that
            object satisfies an arbitrary constraint *or* ``False`` otherwise).

        Returns
        ----------
        SubscriptedIs
            New object encapsulating this data validator.

        Raises
        ----------
        BeartypeValeSubscriptionException
            If either:

            * This class was subscripted by two or more arguments.
            * This class was subscripted by one argument that either:

              * Is *not* callable.
              * Is a C-based rather than pure-Python callable.
              * Is a pure-Python callable accepting two or more arguments.

        .. _PEP 560:
           https://www.python.org/dev/peps/pep-0560
        .. _PEP 593:
           https://www.python.org/dev/peps/pep-0593
        '''

        # If this class was subscripted by either no arguments or two or more
        # arguments, raise an exception. Specifically...
        if isinstance(is_valid, tuple):
            # If this class was subscripted by two or more arguments, raise a
            # human-readable exception.
            if is_valid:
                raise BeartypeValeSubscriptionException(
                    f'{repr(Is)} subscripted by two or more arguments:\n'
                    f'{represent_object(is_valid)}'
                )
            # Else, this class was subscripted by *NO* arguments. In this case,
            # raise a human-readable exception.
            else:
                raise BeartypeValeSubscriptionException(
                    '{repr(Is)} subscripted by empty tuple.')
        # Else, this class was subscripted by a single argument.

        # Dictionary mapping from the name to value of each local attribute
        # referenced in the "is_valid_code" snippet defined below.
        is_valid_code_locals: CallableScope = {}

        # Name of a new parameter added to the signature of each
        # @beartype-decorated wrapper function whose value is this validator,
        # enabling this validator to be called directly in the body of those
        # functions *WITHOUT* imposing additional stack frames.
        is_valid_attr_name = add_func_scope_attr(
            attr=is_valid, attr_scope=is_valid_code_locals)

        # One one-liner to rule them all and in "pdb" bind them.
        return SubscriptedIs(
            is_valid=is_valid,
            # Python code snippet call this validator via that parameter,
            # passed an object to be interpolated into this snippet by
            # downstream logic.
            is_valid_code = f'{is_valid_attr_name}({{obj}})',
            is_valid_code_locals=is_valid_code_locals,
            get_repr=lambda:
                f'Is[{represent_func(func=is_valid, warning_cls=BeartypeValeLambdaWarning)}]',
        )
