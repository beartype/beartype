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
from beartype._util.func.utilfuncmake import copy_func_shallow
from beartype._util.func.utilfunctest import is_func_python
from typing import Any, Callable

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

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
          subscripted (indexed) by a callable accepting a single arbitrary
          object and returning either ``True`` if that object satisfies an
          arbitrary constraint or ``False`` otherwise.

          Formally, the signature of that callable *must* resemble:

          .. _code-block:: python

             def is_object_valid(obj) -> bool:
                 return bool(obj)

          Equivalently, that callable *must* satisfy the type hint
          ``collections.abc.Callable[[typing.Any,], bool]``. Where that is
          *not* the case, an exception is raised.

          Lastly, the :func:`beartype.beartype` decorator only calls that
          callable when the value of the passed parameter or return is an
          instance of the type expected by that parameter or return. That
          callable should safely assume that value to be an instance of that
          type rather than revalidating that value's type (e.g., by passing
          that value and type to the :func:`isinstance` builtin).

    See also the "Examples" subsection below.

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
    def __class_getitem__(
        cls, func: Callable[[Any,], bool]) -> Callable[[Any,], bool]:
        '''
        `PEP 560`_-compliant dunder method dynamically generating a new
        callable from the passed callable suitable for use as a subscription of
        `PEP 593`_-compliant :attr:`typing.Annotated` type hints.

        See the class docstring for usage instructions.

        Parameters
        ----------
        func : Callable[[Any,], bool]
            Caller-defined callable accepting a single arbitrary object and
            returning either ``True`` if that object satisfies an arbitrary
            constraint or ``False`` otherwise.

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
        # If this callable is C-based, raise an exception.
        elif not is_func_python(func):
            raise BeartypeHintIsUsageException(
                f'Class "{cls.__name__}" argument {repr(func)} not callable.')

        #FIXME: Validate this callable to accept exactly one argument.

        # Shallow copy of the passed callable, enabling us to safely
        # monkey-patch this copy *WITHOUT* unsafely modifying this callable.
        func_copy = copy_func_shallow(
            func=func, exception_cls=BeartypeHintIsUsageException)

        #FIXME: Monkey-patch us up.
        # Monkey-patch this copy, notifying the @beartype decorator that this
        # callable is a constraint produced by subscripting this class.

        # Return this copy.
        return func_copy
