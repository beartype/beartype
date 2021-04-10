#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype data validation classes.**

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                              }....................
# All "FIXME:" comments for this submodule reside in this package's "__init__"
# submodule to improve maintainability and readability here.

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeHintIsUsageException
from beartype._util.func.utilfuncarg import get_func_args_len_standard
from beartype._util.func.utilfuncmake import copy_func_shallow
from beartype._util.func.utilfunctest import is_func_python
from typing import Any, Callable

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ HINTS                             }....................
IsValidator = Callable[[Any,], bool]
'''
PEP-compliant type hint matching a **data validator** (i.e., caller-defined
function accepting a single arbitrary object and returning either ``True`` if
that object satisfies an arbitrary constraint or ``False`` otherwise).

Data validators are suitable for subscripting the :class:`Is` class.
'''

# ....................{ CLASSES                           }....................
#FIXME: Unit test us up via the public "beartype.vale.Is" class alias.
#FIXME: Implement as follows:
#* Define the PEP 560-compliant __class_getitem__() class dunder method to:
#  * Accept a single argument, which *MUST* be a callable itself accepting a
#    single positional argument.
#  * Call the beartype._util.func.utilfuncmake.copy_func_shallow() function to
#    create a shallow copy of this function.
#  * Define a new "func_copy.__beartype_is_must = True" attribute on this copy,
#    enabling this copy to be detected as a "Is" subscription.
#  * Return that copy.
#* Define a new is_object_must() tester function *OUTSIDE* this class ala:
#      def is_object_must(obj: object) -> bool:
#          return (
#              callable(obj) and
#              getattr(obj, '__beartype_is_must', False) is True
#          )
#  Actually, call that is_hint_issubscription() instead. *shrug*
#* Define in "_pepsnip":
#      ARG_NAME_CUSTOM_OBJECT = '__beartype_object_{object_id}'
#* Call that tester function from "_pephint" on each argument of an "Annotated"
#  type hint to detect whether that argument is a "Is" subscription; if so,
#  add that argument to "func_wrapper_locals" ala:
#      for hint_child in hint_curr.__args__[1:]:
#          if not is_object_must(hint_child):
#              continue
#
#          hint_child_arg_name = ARG_NAME_CUSTOM_OBJECT.format(
#              object_id=id(hint_child))
#          func_wrapper_locals[hint_child_arg_name: hint_child]
#FIXME: Okay, everything above is great -- *EXCEPT* the objects we generate
#from __class_getitem__(). Currently, we create trivial function copies. That's
#fine for brute-force work, but requires that we diverge from Python syntax by
#replicating core operators. For example, to negate an "Is" constraint, we'd
#then need to create a new distinct "IsNot" constraint; likewise for "or" and
#"and" boolean operations: e.g.,
#    Annotated[str, IsOr[IsEmpty, IsAnd[IsUnquoted, IsNot[IsEmpty]]]]
#That gets real fugly real fast. Instead, we'd strongly prefer to leverage
#existing Python operators: e.g.,
#    Annotated[str, IsEmpty or (IsUnquoted and not IsEmpty)]
#Actually, we can't use verbal operators, because CPython strictly coerces
#their return values in numerous contexts to be booleans. Instead, we want to
#use either arithmetic (e.g., +, -) or set (e.g., |, &) operators. Set
#operators seem to yield an approximate syntax. So, the above then becomes:
#    Annotated[str, IsEmpty | (IsUnquoted & ~IsEmpty)]
#Official documentation for these dunder methods lives at:
#    https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types
#Significantly better, yes? So, how exactly do we go about that? Simple:
#* Design a new "_IsSubscription" class resembling:
#      class _IsSubscription(object):
#          __slots__ = ('_validator',)
#          def __init__(self, is_valid: IsValidator) -> None:
#              # Yup. We can verify this actually works as expected. Wow! :{}
#              self.is_valid = is_valid
#
#          def __and__(self, other: _IsSubscription) -> _IsSubscription:
#              return _IsSubscription(
#                  lambda obj: return self.is_valid(obj) and other.is_valid(obj))
#
#          def __or__(self, other: _IsSubscription) -> _IsSubscription:
#              return _IsSubscription(
#                  lambda obj: return self.is_valid(obj) or other.is_valid(obj))
#
#          def __invert__(self) -> _IsSubscription:
#              return _IsSubscription(lambda obj: return not self.is_valid(obj))
#* Refactor the Is.__class_getitem__() to instantiate and return a new
#  "issubscription = _IsSubscription(func)" instance. Note that we also don't
#  need the copy_func_shallow() function using this approach either. Noice!
#FIXME: Oh, and just make "IsSubscription" public. Then there's no need
#whatsoever for silly testers like is_hint_issubscription(). Yay!

class Is(object):
    '''
    **Beartype data validator** (i.e., class subscripted (indexed) by a
    caller-defined function returning ``True`` only if the single parameter
    passed to that function satisfies arbitrary constraints).

    Callers subscript this class to validate the integrity, consistency, and
    contents of arbitrarily complex scalars, data structures, and third-party
    objects. Subscriptions of this class are PEP-compliant and thus guaranteed
    *never* to violate existing or future standards. Moreover, such
    subscriptions are safely ignorable by *all* static and runtime type
    checkers other than :mod:`beartype` itself.

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
          that object satisfies an arbitrary constraint or ``False``
          otherwise). If that hint is subscripted by:

          * Only one subscription of this class, any passed parameter or
            return satisfies that hint when both:

            * That parameter or return is an instance of the expected type.
            * That data validator returns ``True`` when passed that parameter
              or return.

          * Two or more subscriptions of this class, any passed parameter or
            return satisfies that hint when both:

            * That parameter or return is an instance of the expected type.
            * *All* data validators subscripting *all* subscriptions of this
              class return ``True`` when passed that parameter or return.

          Formally, the signature of each data validator *must* resemble:

          .. _code-block:: python

             def is_object_valid(obj) -> bool:
                 return bool(obj)

          Equivalently, each validator *must* satisfy the type hint
          ``collections.abc.Callable[[typing.Any,], bool]``. Where that is
          *not* the case, an exception is raised.

          Note that:

          * The name of each validator is irrelevant. Indeed, most validators
            are defined as nameless lambda functions for convenience.
          * Each validator is called *only* when the value of the passed
            parameter or return is an instance of the type expected by that
            parameter or return. Each validator may thus safely assume that
            value to be an instance of that type rather than revalidating that
            value's type (e.g., by passing that value and type to the
            :func:`isinstance` builtin).

    For example, this type hint accepts only non-empty strings:

    .. _code-block:: python

       Annotated[str, Is[lambda text: bool(text)]]

    Subscriptions (indexations) of this class also support an expressive
    domain-specific language (DSL) leveraging Pythonic math operators, enabling
    callers to dynamically combine and negate existing subscriptions *without*
    redefining those subscriptions and thus violating DRY_:

    * **Negation** (i.e., ``not``). Negating a single subscription with the
      ``~`` operator returns ``True`` only when that subscription returns
      ``False``. For example, this type hint accepts only strings containing
      *no* periods:

      .. _code-block:: python

         Annotated[str, ~Is[lambda text: '.' in text]]

    * **Conjunction** (i.e., ``and``). Conjunctively combining two or more
      subscriptions with the ``&`` operator returns ``True`` only when all
      subscriptions return ``True``. For example, this type hint accepts only
      non-empty strings containing *no* periods:

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

      .. _code-block:: python

         Annotated[str, (
             ~Is[lambda text: bool(text)] |
              Is[lambda text: '.' in text]
         )]

    See also the **Examples** subsection below.

    Caveats
    ----------
    **This class is currently only supported by the** :func:`beartype.beartype`
    **decorator.** All other static and runtime type checkers will silently
    ignore subscriptions of this class subscripting `PEP 593`_-compliant
    :attr:`typing.Annotated` type hints.

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
    an :exc:`BeartypeHintIsUsageException` exception.

    **This class is only usable when subscripted in subscriptions of**
    `PEP 593`_-compliant :attr:`typing.Annotated` **type hints**. Attempting to
    use this class in any other context will raise an exception. Notably,
    attempting to directly annotate a callable with a subscription of this
    class will raise an :exc:`beartype.roar.BeartypeDecorHintNonPepException`.

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

    .. _DRY:
       https://en.wikipedia.org/wiki/Don%27t_repeat_yourself
    .. _PEP 593:
       https://www.python.org/dev/peps/pep-0593
    '''

    # ..................{ INITIALIZERS                      }..................
    def __new__(cls, *args, **kwargs):
        '''
        Unconditionally raise an exception on attempted instantiation.

        Like standard type hint singletons (e.g., :attr:`typing.Union`), this
        class is *only* intended to be subscripted (indexed).

        Raises
        ----------
        BeartypeHintIsUsageException
            Always.
        '''

        # Murderbot would know what to do here.
        raise BeartypeHintIsUsageException(
            f'Class "{cls.__name__}" not instantiable; '
            f'consider subscripting this class instead '
            f'(e.g., "{cls.__name__}[...]").'
        )

    # ..................{ GETTERS                           }..................
    #FIXME: Revise in accordance with above.
    def __class_getitem__(cls, func: IsValidator) -> IsValidator:
        '''
        `PEP 560`_-compliant dunder method dynamically generating a new
        callable from the passed callable suitable for use as a subscription of
        `PEP 593`_-compliant :attr:`typing.Annotated` type hints.

        See the class docstring for usage instructions.

        Parameters
        ----------
        func : Callable[[Any,], bool]
            **Data validator** (i.e., caller-defined function accepting a
            single arbitrary object and returning either ``True`` if that
            object satisfies an arbitrary constraint or ``False`` otherwise).

        Raises
        ----------
        BeartypeHintIsUsageException
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
        # arguments...
        if isinstance(func, tuple):
            # If this class was subscripted by two or more arguments, raise a
            # human-readable exception.
            if func:
                raise BeartypeHintIsUsageException(
                    f'Class "{cls.__name__}" subscripted by two or more '
                    f'arguments {repr(func)}.'
                )
            # Else, this class was subscripted by *NO* arguments. In this case,
            # raise a human-readable exception.
            else:
                raise BeartypeHintIsUsageException(
                    f'Class "{cls.__name__}" subscripted by empty tuple.')
        # Else, the this class was subscripted by a single argument.
        #
        # If this argument is uncallable, raise a human-readable exception.
        elif not callable(func):
            raise BeartypeHintIsUsageException(
                f'Class "{cls.__name__}" argument {repr(func)} not callable.')
        # Else, this argument is callable.
        #
        # If this callable is C-based, raise a human-readable exception.
        elif not is_func_python(func):
            raise BeartypeHintIsUsageException(
                f'Class "{cls.__name__}" argument {repr(func)} not '
                f'pure-Python (i.e., implemented in C or another language).'
            )
        # Else, this callable is pure-Python.
        #
        # If this callable does *NOT* accept exactly one argument, raise a
        # human-readable exception.
        elif get_func_args_len_standard(func) != 1:
            raise BeartypeHintIsUsageException(
                f'Class "{cls.__name__}" argument {repr(func)} accepts '
                f'{get_func_args_len_standard(func)} arguments rather than 1.'
            )
        # Else, this callable accepts exactly one argument. Since no further
        # validation can be performed on this callable without unsafely calling
        # that callable, we accept this callable as is for now.

        #FIXME: Create an instance of "_IsSubscription" instead. See above!
        # Shallow copy of the passed callable, enabling us to safely
        # monkey-patch this copy *WITHOUT* unsafely modifying this callable.
        func_copy = copy_func_shallow(
            func=func, exception_cls=BeartypeHintIsUsageException)

        # Return this copy.
        return func_copy
