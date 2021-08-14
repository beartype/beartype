#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`593`-compliant type hint utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeDecorHintPep593Exception
from beartype._data.hint.pep.sign.datapepsigncls import HintSign
from beartype._data.hint.pep.sign.datapepsigns import HintSignAnnotated
from beartype._vale._valesub import _SubscriptedIs
from typing import Any, Optional, Tuple

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ VALIDATORS                        }....................
#FIXME: Unit test us up, please.
def die_unless_hint_pep593(hint: object) -> None:
    '''
    Raise an exception unless the passed object is a :pep:`593`-compliant
    **type metahint** (i.e., subscription of the :attr:`typing.Annotated`
    singleton).

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Raises
    ----------
    BeartypeDecorHintPep593Exception
        If this object is *not* a :pep:`593`-compliant type metahint.
    '''

    # If this hint is *NOT* PEP 593-compliant, raise an exception.
    if not is_hint_pep593(hint):
        raise BeartypeDecorHintPep593Exception(
            f'PEP 593 type hint {repr(hint)} not "typing.Annotated".')

# ....................{ TESTERS                           }....................
#FIXME: This tester is now trivially silly. Excise as follows:
#* Replace all calls to this tester with tests resembling:
#      get_hint_pep_sign_or_none(hint) is HintSignAnnotated
#* Excise this tester.
def is_hint_pep593(hint: object) -> bool:
    '''
    ``True`` only if the passed object is a :pep:`593`-compliant **type
    metahint** (i.e., subscription of the :attr:`typing.Annotated` singleton).

    This tester is memoized for efficiency.

    Parameters
    ----------
    hint : object
        Object to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a :pep:`593`-compliant user-defined
        type metahint.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import (
        get_hint_pep_sign_or_none)

    # Return true only if the machine-readable representation of this object
    # implies this object to be a PEP 593-compliant type hint hint.
    #
    # Note that this approach has been intentionally designed to apply to
    # arbitrary and hence possibly PEP-noncompliant type hints. Notably, this
    # approach avoids the following equally applicable but considerably less
    # efficient heuristic:
    #    return is_hint_pep(hint) and get_hint_pep_sign(hint) is HintSignAnnotated
    return get_hint_pep_sign_or_none(hint) is HintSignAnnotated


def is_hint_pep593_ignorable_or_none(
    hint: object, hint_sign: HintSign) -> Optional[bool]:
    '''
    ``True`` only if the passed object is a :pep:`593`-compliant ignorable type
    hint, ``False`` only if this object is a :pep:`593`-compliant unignorable
    type hint, and ``None`` if this object is *not* :pep:`593`-compliant.

    Specifically, this tester function returns ``True`` only if this object is
    the :data:`Annotated` singleton whose first subscripted argument is an
    ignorable type hints (e.g., ``typing.Annotated[typing.Any, bool]``).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as this tester is only safely callable
    by the memoized parent
    :func:`beartype._util.hint.utilhinttest.is_hint_ignorable` tester.

    Parameters
    ----------
    hint : object
        Type hint to be inspected.
    hint_sign : HintSign
        **Sign** (i.e., arbitrary object uniquely identifying this hint).

    Returns
    ----------
    Optional[bool]
        Either:

        * If this object is :pep:`593`-compliant:

          * If this object is a ignorable, ``True``.
          * Else, ``False``.

        * If this object is *not* :pep:`593`-compliant, ``None``.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.utilhinttest import is_hint_ignorable
    # print(f'!!!!!!!Received 593 hint: {repr(hint)} [{repr(hint_sign)}]')

    # Return either...
    return (
        # If this hint is annotated, true only if the PEP-compliant child type
        # hint annotated by this hint hint is ignorable (e.g., the "Any" in
        # "Annotated[Any, 50, False]").
        is_hint_ignorable(get_hint_pep593_metahint(hint))
        if hint_sign is HintSignAnnotated else
        # Else, "None".
        None
    )

# ....................{ TESTERS ~ beartype                }....................
def is_hint_pep593_beartype(hint: Any) -> bool:
    '''
    ``True`` only if the first argument subscripting the passed
    :pep:`593`-compliant :attr:`typing.Annotated` type hint is
    :mod:`beartype`-specific (e.g., instance of the :class:`_SubscriptedIs`
    class produced by subscripting (indexing) the :class:`Is` class).

    Parameters
    ----------
    hint : Any
        :pep:`593`-compliant :attr:`typing.Annotated` type hint to be
        inspected.

    Returns
    ----------
    bool
        ``True`` only if the first argument subscripting this hint is
        :mod:`beartype`-specific.

    Raises
    ----------
    BeartypeDecorHintPep593Exception
        If this object is *not* a :pep:`593`-compliant type metahint.
    '''

    # If this object is *NOT* a PEP 593-compliant type metahint, raise an
    # exception.
    die_unless_hint_pep593(hint)
    # Else, this object is a PEP 593-compliant type metahint.

    # Attempt to return true only if the first argument subscripting this hint
    # is beartype-specific.
    #
    # Note that the "__metadata__" dunder attribute is both guaranteed to exist
    # for metahints *AND* be a non-empty tuple of arbitrary objects: e.g.,
    #     >>> from typing import Annotated
    #     >>> Annotated[int]
    #     TypeError: Annotated[...] should be used with at least two
    #     arguments (a type and an annotation).
    try:
        return isinstance(hint.__metadata__[0], _SubscriptedIs)
    # If the metaclass of the first argument subscripting this hint overrides
    # the __isinstancecheck__() dunder method to raise an exception, silently
    # ignore this exception by returning false instead.
    except:
        return False

# ....................{ GETTERS                           }....................
#FIXME: Unit test us up, please.
def get_hint_pep593_metadata(hint: Any) -> Tuple[Any, ...]:
    '''
    Tuple of one or more arbitrary objects annotating the passed
    :pep:`593`-compliant **type metahint** (i.e., subscription of the
    :attr:`typing.Annotated` singleton).

    Specifically, this getter returns *all* arguments subscripting this
    metahint excluding the first, which conveys its own semantics and is thus
    returned by the :func:`get_hint_pep593_metahint` getter.

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        `PEP 593`-compliant type metahint to be inspected.

    Returns
    ----------
    type
        Tuple of one or more arbitrary objects annotating this metahint.

    Raises
    ----------
    BeartypeDecorHintPep593Exception
        If this object is *not* a :pep:`593`-compliant type metahint.

    See Also
    ----------
    :func:`is_hint_pep593`
        Further commentary.
    :func:`get_hint_pep593_metahint`
        Related getter.
    '''

    # If this object is *NOT* a metahint, raise an exception.
    die_unless_hint_pep593(hint)
    # Else, this object is a metahint.

    # Return the tuple of one or more objects annotating this metahint.
    return hint.__metadata__


#FIXME: Unit test us up, please.
def get_hint_pep593_metahint(hint: Any) -> Any:
    '''
    PEP-compliant type hint annotated by the passed :pep:`593`-compliant **type
    metahint** (i.e., subscription of the :attr:`typing.Annotated` singleton).

    Specifically, this getter returns the first argument subscripting this
    metahint. By design, this argument is guaranteed to be a PEP-compliant type
    hint. Note that although that hint *may* be a standard class, this is *not*
    necessarily the case.

    This getter is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : object
        :pep:`593`-compliant type metahint to be inspected.

    Returns
    ----------
    Any
        PEP-compliant type hint annotated by this metahint.

    Raises
    ----------
    BeartypeDecorHintPep593Exception
        If this object is *not* a :pep:`593`-compliant type metahint.

    See Also
    ----------
    :func:`is_hint_pep593`
        Further commentary.
    :func:`get_hint_pep593_metadata`
        Related getter.
    '''

    # If this object is *NOT* a metahint, raise an exception.
    die_unless_hint_pep593(hint)
    # Else, this object is a metahint.

    # Return the standard class annotated by this metahint.
    #
    # Note that most edge-case PEP-compliant type hints store their data in
    # hint-specific dunder attributes (e.g., "__supertype__" for new type
    # aliases, "__forward_arg__" for forward references). Some, however, coopt
    # and misuse standard dunder attributes commonly used for entirely
    # different purposes. PEP 593-compliant type metahints the latter sort,
    # preferring to store their class in the standard "__origin__" attribute
    # commonly used to store the origin type of type hints originating from a
    # standard class rather than in a metahint-specific dunder attribute.
    return hint.__origin__
