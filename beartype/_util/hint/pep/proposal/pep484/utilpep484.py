#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-compliant type hint utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._cave._cavefast import NoneType

# Intentionally import PEP 484-compliant "typing" type hint factories rather
# than possibly PEP 585-compliant "beartype.typing" type hint factories.
from typing import (
    Generic,
    Tuple,
)

# ....................{ HINTS                              }....................
HINT_PEP484_TUPLE_EMPTY = Tuple[()]
'''
:pep:`484`-compliant empty fixed-length tuple type hint.
'''

# ....................{ TESTERS ~ ignorable                }....................
#FIXME: Shift into a more appropriate submodule, please.
def is_hint_pep484585_generic_ignorable(hint: object) -> bool:
    '''
    :data:`True` only if the passed :pep:`484`- or :pep:`585`-compliant generic
    is ignorable.

    Specifically, this tester ignores *all* parametrizations of the
    :class:`typing.Generic` abstract base class (ABC) by one or more type
    variables. As the name implies, this ABC is generic and thus fails to impose
    any meaningful constraints. Since a type variable in and of itself also
    fails to impose any meaningful constraints, these parametrizations are
    safely ignorable in all possible contexts: e.g.,

    .. code-block:: python

       from typing import Generic, TypeVar
       T = TypeVar('T')
       def noop(param_hint_ignorable: Generic[T]) -> T: pass

    This tester is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as this tester is only safely callable by
    the memoized parent
    :func:`beartype._util.hint.utilhinttest.is_hint_ignorable` tester.

    Parameters
    ----------
    hint : object
        Type hint to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this :pep:`484`-compliant type hint is ignorable.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_origin_or_none
    # print(f'Testing generic hint {repr(hint)} deep ignorability...')

    # If this generic is the "typing.Generic" superclass directly parametrized
    # by one or more type variables (e.g., "typing.Generic[T]"), return true.
    #
    # Note that we intentionally avoid calling the
    # get_hint_pep_origin_type_isinstanceable_or_none() function here, which has
    # been intentionally designed to exclude PEP-compliant type hints
    # originating from "typing" type origins for stability reasons.
    if get_hint_pep_origin_or_none(hint) is Generic:
        # print(f'Testing generic hint {repr(hint)} deep ignorability... True')
        return True
    # Else, this generic is *NOT* the "typing.Generic" superclass directly
    # parametrized by one or more type variables and thus *NOT* an ignorable
    # non-protocol.
    #
    # Note that this condition being false is *NOT* sufficient to declare this
    # hint to be unignorable. Notably, the origin type originating both
    # ignorable and unignorable protocols is "Protocol" rather than "Generic".
    # Ergo, this generic could still be an ignorable protocol.
    # print(f'Testing generic hint {repr(hint)} deep ignorability... False')

    #FIXME: Probably insufficient. *shrug*
    return False


#FIXME: Remove this *AFTER* properly supporting type variables. For now,
#ignoring type variables is required ta at least shallowly support generics
#parametrized by one or more type variables.
def is_hint_pep484_typevar_ignorable(hint: object) -> bool:
    '''
    :data:`True` unconditionally.

    This tester currently unconditionally ignores *all* :pep:`484`-compliant
    type variables, which require non-trivial and currently unimplemented
    code generation support.

    This tester is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as this tester is only safely callable by
    the memoized parent
    :func:`beartype._util.hint.utilhinttest.is_hint_ignorable` tester.

    Parameters
    ----------
    hint : object
        Type hint to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this :pep:`484`-compliant type hint is ignorable.
    '''

    # Ignore *ALL* PEP 484-compliant type variables.
    return True


#FIXME: Shift into a more appropriate submodule, please.
def is_hint_pep484604_union_ignorable(hint: object) -> bool:
    '''
    :data:`True` only if the passed :pep:`484`- or :pep:`604`-compliant union is
    ignorable.

    Specifically, this tester ignores the :obj:`typing.Optional` or
    :obj:`typing.Union` singleton subscripted by one or more ignorable type
    hints (e.g., ``typing.Union[typing.Any, bool]``). Why? Because unions are by
    definition only as narrow as their widest child hint. However, shallowly
    ignorable type hints are ignorable precisely because they are the widest
    possible hints (e.g., :class:`object`, :attr:`typing.Any`), which are so
    wide as to constrain nothing and convey no meaningful semantics. A union of
    one or more shallowly ignorable child hints is thus the widest possible
    union, which is so wide as to constrain nothing and convey no meaningful
    semantics. Since there exist a countably infinite number of possible
    :data:`Union` subscriptions by one or more ignorable type hints, these
    subscriptions *cannot* be explicitly listed in the
    :data:`beartype._data.hint.pep.datapeprepr.HINTS_REPR_IGNORABLE_SHALLOW`
    frozenset. Instead, these subscriptions are dynamically detected by this
    tester at runtime and thus referred to as **deeply ignorable type hints.**

    This tester is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as this tester is only safely callable by
    the memoized parent
    :func:`beartype._util.hint.utilhinttest.is_hint_ignorable` tester.

    Parameters
    ----------
    hint : object
        Type hint to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this :pep:`484`-compliant type hint is ignorable.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_args
    from beartype._util.hint.utilhinttest import is_hint_ignorable

    # Return true only if one or more child hints of this union are recursively
    # ignorable. See the function docstring.
    return any(
        is_hint_ignorable(hint_child) for hint_child in get_hint_pep_args(hint))

# ....................{ REDUCERS                           }....................
#FIXME: Replace the ambiguous parameter:
#* "hint: object" with the unambiguous parameter "hint: Literal[None]" *AFTER*
#  we drop support for Python 3.7. *sigh*

# Note that this reducer is intentionally typed as returning "type" rather than
# "NoneType". While the former would certainly be preferable, mypy erroneously
# emits false positives when this reducer is typed as returning "NoneType":
#     beartype/_util/hint/pep/proposal/pep484/utilpep484.py:190: error: Variable
#     "beartype._cave._cavefast.NoneType" is not valid as a type [valid-type]
def reduce_hint_pep484_none(hint: object, *args, **kwargs) -> type:
    '''
    Reduce the passed :pep:`484`-compliant :data:`None` type hint to the type of
    that type hint (i.e., the builtin :class:`types.NoneType` class).

    While *not* explicitly defined by the :mod:`typing` module, :pep:`484`
    explicitly supports this singleton:

        When used in a type hint, the expression :data:`None` is considered
        equivalent to ``type(None)``.

    This reducer is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        Type variable to be reduced.

    All remaining passed arguments are silently ignored.

    Returns
    -------
    NoneType
        Type of the :data:`None` singleton.
    '''
    assert hint is None, f'Type hint {hint} not "None" singleton.'

    # Unconditionally return the type of the "None" singleton.
    return NoneType
