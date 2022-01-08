#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`593`-compliant type hint utilities.

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
from beartype.roar import BeartypeDecorHintPep593Exception
from beartype._data.hint.pep.sign.datapepsigncls import HintSign
from beartype._data.hint.pep.sign.datapepsigns import HintSignAnnotated
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_7
from beartype._data.datatyping import TypeException
from typing import Any, Optional, Tuple

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ VALIDATORS                        }....................
#FIXME: Pass "exception_prefix" to all calls of this validator.
def die_unless_hint_pep593(
    # Mandatory parameters.
    hint: object,

    # Optional parameters.
    exception_cls: TypeException = BeartypeDecorHintPep593Exception,
    exception_prefix: str = '',
) -> None:
    '''
    Raise an exception of the passed type unless the passed object is a
    :pep:`593`-compliant **type metahint** (i.e., subscription of either the
    :attr:`typing.Annotated` or :attr:`typing_extensions.Annotated` type hint
    factories).

    Parameters
    ----------
    hint : object
        Type hint to be inspected.
    exception_cls : TypeException
        Type of exception to be raised. Defaults to
        :exc:`BeartypeDecorHintPep593Exception`.
    exception_prefix : str, optional
        Human-readable substring prefixing the representation of this object in
        the exception message. Defaults to the empty string.

    Raises
    ----------
    BeartypeDecorHintPep593Exception
        If this object is *not* a :pep:`593`-compliant type metahint.
    '''

    # If this hint is *NOT* PEP 593-compliant, raise an exception.
    if not is_hint_pep593(hint):
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')
        raise exception_cls(
            f'{exception_prefix}type hint {repr(hint)} not PEP 593-compliant '
            f'(e.g., "typing.Annotated[...]", '
            f'"typing_extensions.Annotated[...]").'
        )

# ....................{ TESTERS                           }....................
#FIXME: Unit test us up.
def is_hint_pep593(hint: Any) -> bool:
    '''
    ``True`` only if the passed object is a :pep:`593`-compliant **type
    metahint** (i.e., subscription of either the :attr:`typing.Annotated` or
    :attr:`typing_extensions.Annotated` type hint factories).

    Parameters
    ----------
    hint : Any
        Type hint to be inspected.

    Returns
    ----------
    bool
        ``True`` only if this object is a :pep:`593`-compliant type metahint.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.utilpepget import get_hint_pep_sign_or_none

    # Return true only if this hint is PEP 593-compliant.
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
    :mod:`beartype`-specific (e.g., instance of the :class:`BeartypeValidator`
    class produced by subscripting (indexing) the :class:`Is` class).

    Parameters
    ----------
    hint : Any
        :pep:`593`-compliant type hint to be inspected.

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

    # Defer heavyweight imports.
    from beartype.vale._core._valecore import BeartypeValidator

    # If this object is *NOT* a PEP 593-compliant type metahint, raise an
    # exception.
    die_unless_hint_pep593(hint)
    # Else, this object is a PEP 593-compliant type metahint.

    # Attempt to...
    try:
        # Tuple of one or more arbitrary objects annotating this metahint.
        hint_metadata = get_hint_pep593_metadata(hint)

        # Return true only if the first such object is a beartype validator.
        # Note this object is guaranteed to exist by PEP 593 design.
        # print(f'Checking first PEP 593 type hint {repr(hint)} arg {repr(hint_metadata[0])}...')
        return isinstance(hint_metadata[0], BeartypeValidator)
    # If the metaclass of the first argument subscripting this hint overrides
    # the __isinstancecheck__() dunder method to raise an exception, silently
    # ignore this exception by returning false instead.
    except:
        return False

# ....................{ GETTERS                           }....................
# If the active Python interpreter targets Python >= 3.7, define these getters
# to return standard dunder attributes.
if IS_PYTHON_AT_LEAST_3_7:
    #FIXME: Unit test us up, please.
    def get_hint_pep593_metadata(hint: Any) -> Tuple[Any, ...]:

        # If this object is *NOT* a metahint, raise an exception.
        die_unless_hint_pep593(hint)
        # Else, this object is a metahint.

        # Return the tuple of one or more objects annotating this metahint. By
        # design, this tuple is guaranteed to be non-empty: e.g.,
        #     >>> from typing import Annotated
        #     >>> Annotated[int]
        #     TypeError: Annotated[...] should be used with at least two
        #     arguments (a type and an annotation).
        return hint.__metadata__


    #FIXME: Unit test us up, please.
    def get_hint_pep593_metahint(hint: Any) -> Any:

        # If this object is *NOT* a metahint, raise an exception.
        die_unless_hint_pep593(hint)
        # Else, this object is a metahint.

        # Return the PEP-compliant type hint annotated by this metahint.
        #
        # Note that most edge-case PEP-compliant type hints store their data in
        # hint-specific dunder attributes (e.g., "__supertype__" for new type
        # aliases, "__forward_arg__" for forward references). Some, however,
        # coopt and misuse standard dunder attributes commonly used for
        # entirely different purposes. PEP 593-compliant type metahints are the
        # latter sort, preferring to store their class in the standard
        # "__origin__" attribute commonly used to store the origin type of type
        # hints originating from a standard class rather than in a
        # metahint-specific dunder attribute.
        return hint.__origin__
# Else, the active Python interpreter targets Python 3.6. In this case, define
# this getter to return slices of the non-standard "__args__" dunder attribute
# declared by the third-party "typing_extensions.Annotated" type hint factory.
else:
    def get_hint_pep593_metadata(hint: Any) -> Tuple[Any, ...]:

        # If this object is *NOT* a metahint, raise an exception.
        die_unless_hint_pep593(hint)
        # Else, this object is a metahint.

        # Return the tuple of one or more objects annotating this metahint.
        # Since this is Python 3.6, this metahint *MUST* be a subscription of
        # the third-party "typing_extensions.Annotated" type hint factory.
        # Under Python 3.6, this factory stores this tuple as the second item
        # of the non-standard "__args__" dunder attribute tuple. (I sigh.)
        return hint.__args__[1]


    def get_hint_pep593_metahint(hint: Any) -> Any:

        # If this object is *NOT* a metahint, raise an exception.
        die_unless_hint_pep593(hint)
        # Else, this object is a metahint.

        # Return the PEP-compliant type hint annotated by this metahint.
        return hint.__args__[0]


get_hint_pep593_metadata.__doc__ = '''
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
    :func:`get_hint_pep593_metahint`
        Related getter.
    '''


get_hint_pep593_metahint.__doc__ = '''
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
    :func:`get_hint_pep593_metadata`
        Related getter.
    '''
