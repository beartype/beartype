#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
# See "LICENSE" for further details.

'''
**Beartype decorator** `PEP 484`_ **testers.**

This private submodule is *not* intended for importation by downstream callers.

.. _PEP 484:
   https://www.python.org/dev/peps/pep-0484
'''

# ....................{ IMPORTS                           }....................
# from beartype.cave import (ClassType,)
from beartype.roar import BeartypeDecorPep484TypeUnsupportedException
from beartype._util import utilhint
from beartype._util.utilcache import callable_cached
from typing import TypeVar

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ EXCEPTIONS                        }....................
def die_if_typing_unsupported(hint: object) -> None:
    '''
    Raise an exception if the passed object is a `PEP 484`_ type (i.e., class
    or object declared by the stdlib :mod:`typing` module) currently
    unsupported by the :func:`beartype.beartype` decorator.

    This includes:

    * **Type variables** (i.e., instances of the :mod:`typing.TypeVar` class).
    * `PEP 484`_ types parametrized by one or more type variables (e.g.,
      ``typing.List[typing.TypeVar['T']]``).

    Parameters
    ----------
    hint : object
        Object to be validated.

    Raises
    ----------
    BeartypeDecorPep484TypeUnsupportedException
        If this object is an unsupported `PEP 484`_ type.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    # Template for exception messages raised by this function.
    EXCEPTION_MESSAGE_TEMPLATE = '{} currently unsupported by @beartype.'

    # If this object is either a PEP 484 type variable *OR* PEP 484 type
    # parametrized by one or more such variables, raise an exception.
    if is_hint_typing_typevar(hint):
        raise BeartypeDecorPep484TypeUnsupportedException(
            EXCEPTION_MESSAGE_TEMPLATE.format(
                'Type variable {!r}'.format(hint)))
    # Else if this object is a PEP 484 type parametrized by one or more such
    # variables, raise an exception.
    elif is_hint_typing_args_typevar(hint):
        raise BeartypeDecorPep484TypeUnsupportedException(
            EXCEPTION_MESSAGE_TEMPLATE.format(
                'Generic parametrized by '
                'one or more type variables {!r}'.format(hint)))

# ....................{ TESTERS ~ typevar                 }....................
#FIXME: Consider excising. Unsure if we actually require this. *sigh*
@callable_cached
def is_hint_typing_typevarish(hint: object) -> bool:
    '''
    ``True`` only if the passed object is either a `PEP 484`_ **type variable**
    (i.e., instance of the :mod:`typing.TypeVar` class) *or* a `PEP 484`_ type
    parametrized by one or more type variables (e.g.,
    ``typing.List[typing.TypeVar['T']]``).

    For efficiency, this tester is memoized.

    Motivation
    ----------
    Since type variables are not themselves types but rather placeholders
    dynamically replaced with types by type checkers according to various
    arcane heuristics, both type variables and types parametrized by type
    variables warrant special-purpose handling.

    Parameters
    ----------
    hint : object
        Object type to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is either a type variable or `PEP 484`_
        type parametrized by one or more type variables.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    # Return true only if this type either...
    return (
        # Is a type variable *OR*...
        is_hint_typing_typevar(hint) or
        # This is a "typing" type parametrized by one or more type variables.
        is_hint_typing_args_typevar(hint)
    )


def is_hint_typing_typevar(hint: object) -> bool:
    '''
    ``True`` only if the passed object either is a `PEP 484`_ **type variable**
    (i.e., instance of the :mod:`typing.TypeVar` class).

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a type variable.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    # Return true only if this is a type variable.
    return isinstance(hint, TypeVar)


@callable_cached
def is_hint_typing_args_typevar(hint: object) -> bool:
    '''
    ``True`` only if the passed object is a `PEP 484`_ type parametrized by one
    or more type variables (e.g., ``typing.List[typing.TypeVar['T']]``).

    For efficiency, this tester is memoized.

    Parameters
    ----------
    hint : object
        Object type to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is `PEP 484`_ type parametrized by one or
        more type variables.

    .. _PEP 484:
       https://www.python.org/dev/peps/pep-0484
    '''

    # Return true only if this is a "typing" type parametrized by one or more
    # type variables, trivially detected by testing whether the tuple of all
    # type variables parametrizing this "typing" type if this type is a generic
    # (e.g., "typing._GenericAlias" subtype) *OR* the empty tuple otherwise is
    # non-empty.
    #
    # Note that the "typing._GenericAlias.__parameters__" dunder attribute
    # tested here is defined by the typing._collect_type_vars() function at
    # subtype declaration time. Yes, this is insane. Yes, this is PEP 484.
    return (
        utilhint.is_hint_typing(hint) and
        len(getattr(hint, '__parameters__', ())) > 0
    )
