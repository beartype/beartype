#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`- and :pep:`585`-compliant **generic type hint
reducers** (i.e., low-level callables converting various kinds of high-level
:pep:`484`- and :pep:`585`-compliant generic types to lower-level type hints
more readily consumable by :mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._data.hint.datahintpep import Hint
from beartype._check.metadata.metasane import HintOrHintSanifiedData

# ....................{ REDUCERS                           }....................
def reduce_hint_pep484585_generic_subscripted(
    hint: Hint,
    exception_prefix: str,
    **kwargs
) -> HintOrHintSanifiedData:
    '''
    Reduce the passed :pep:`484`- or :pep:`585`-compliant **subscripted
    generic** (i.e., object subscripted by one or more child type hints
    originating from a type originally subclassing at least one subscripted
    :pep:`484`- or :pep:`585`-compliant pseudo-superclass) to a more suitable
    type hint better supported by :mod:`beartype` if necessary.

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as reducers cannot be memoized.

    Parameters
    ----------
    hint : Hint
        Subscripted generic to be reduced.
    exception_prefix : str, optional
        Human-readable substring prefixing raised exception messages.

    All remaining passed keyword parameters are silently ignored.

    Returns
    -------
    HintOrHintSanifiedData
        Either:

        * If the unsubscripted hint (e.g., :class:`typing.Generic`) originating
          this subscripted hint (e.g., ``typing.Generic[S, T]``) is
          unparametrized by type variables, that unsubscripted hint as is.
        * Else, that unsubscripted hint is parametrized by one or more type
          variables. In this case, the **sanified type hint metadata** (i.e.,
          :class:`.HintSanifiedData` object) describing this reduction.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.proposal.pep484.pep484typevar import (
        reduce_hint_pep484_subscripted_typevar_to_hint)

    # Useful PEP 544-compliant unsubscripted protocol possibly reduced from this
    # useless PEP 484- or 585-compliant subscripted IO generic if this hint is a
    # subscripted IO generic *OR* this hint as is otherwise.
    #
    # Note that we reduce this subscripted IO generic *BEFORE* stripping all
    # child hints subscripting this IO generic, as this reducers requires these
    # child hints to correctly reduce this IO generic.
    hint_reduced = _reduce_hint_pep484585_generic_io(
        hint=hint, exception_prefix=exception_prefix)

    # If this hint was *NOT* reduced to an unsubscripted generic from this
    # subscripted IO generic...
    if hint is hint_reduced:
        # # Reduce this subscripted generic to:
        # # * The semantically useful unsubscripted generic originating this
        # #   semantically useless subscripted generic.
        # # * The type variable lookup table mapping all type variables
        # #   parametrizing this unsubscripted generic to all non-type variable
        # #   hints subscripting this subscripted generic.
        # print(f'[reduce_hint_pep484585_generic_subscripted] Reducing subscripted generic {repr(hint)}...')
        # hint_reduced = reduce_hint_pep484_subscripted_typevar_to_hint(hint)
        # print(f'[reduce_hint_pep484585_generic_subscripted] ...to unsubscripted generic {repr(hint_reduced)}.')

        # #FIXME: Excise in favour of the above. For unknown reasons, the above is
        # #currently inducing an infinite wait under Python 3.9. *sigh*
        from beartype._util.hint.pep.utilpepget import get_hint_pep_origin

        # Unsubscripted type alias originating this subscripted hint.
        hint_reduced = get_hint_pep_origin(hint)
    # Else, this hint was reduced to an unsubscripted generic from this
    # subscripted IO generic. In this case, preserve this reduction.

    # Return this reduced hint.
    return hint_reduced


def reduce_hint_pep484585_generic_unsubscripted(
    hint: Hint, exception_prefix: str, **kwargs) -> Hint:
    '''
    Reduce the passed :pep:`484`- or :pep:`585`-compliant **unsubscripted
    generic** (i.e., type originally subclassing at least one unsubscripted
    :pep:`484`- or :pep:`585`-compliant pseudo-superclass) to a more suitable
    type hint better supported by :mod:`beartype` if necessary.

    This reducer is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as reducers cannot be memoized.

    Parameters
    ----------
    hint : Hint
        Subscripted generic to be reduced.
    exception_prefix : str, optional
        Human-readable label prefixing the representation of this object in the
        exception message.

    All remaining passed arguments are silently ignored.

    Returns
    -------
    Hint
        This unsubscripted generic possibly reduced to a more suitable hint.
    '''

    # Hint possibly reduced from this useless unsubscripted IO generic if this
    # hint is an unsubscripted IO generic *OR* this hint as is otherwise.
    hint_reduced = _reduce_hint_pep484585_generic_io(
        hint=hint, exception_prefix=exception_prefix)

    # Return this possibly reduced hint.
    return hint_reduced

# ....................{ PRIVATE ~ reducers                 }....................
def _reduce_hint_pep484585_generic_io(
    hint: Hint,
    exception_prefix: str,
    **kwargs
) -> Hint:
    '''
    Reduce the passed :pep:`484`- or :pep:`585`-compliant **standard IO
    generic** (i.e., standard :obj:`typing.IO` generic (in either subscripted or
    unsubscripted forms) *or* the standard :obj:`BinaryIO` or :obj:`TextIO`
    unsubscripted generics) to a beartype-specific :pep:`544`-compliant protocol
    implementing this generic if this generic is a standard IO generic *or*
    silently ignore this generic otherwise.

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as reducers cannot be memoized.

    Parameters
    ----------
    hint : Hint
        Standard IO generic to be reduced.
    exception_prefix : str, optional
        Human-readable substring prefixing raised exception messages.

    All remaining passed keyword parameters are silently ignored.

    Returns
    -------
    Hint
        This subscripted generic possibly reduced to a more suitable hint.
    '''

    # Avoid circular import dependencies.
    from beartype._util.hint.pep.proposal.pep544 import (
        is_hint_pep484_generic_io,
        reduce_hint_pep484_generic_io_to_pep544_protocol,
    )

    # If this hint is a PEP 484-compliant IO generic base class *AND* the active
    # Python interpreter targets Python >= 3.8 and thus supports PEP
    # 544-compliant protocols, reduce this functionally useless hint to the
    # corresponding functionally useful beartype-specific PEP 544-compliant
    # protocol implementing this hint.
    #
    # Note that PEP 484-compliant IO generic base classes are technically
    # usable under Python < 3.8 (e.g., by explicitly subclassing those classes
    # from third-party classes). Ergo, we can neither safely emit warnings nor
    # raise exceptions on visiting these classes under *ANY* Python version.
    if is_hint_pep484_generic_io(hint):
        # print(f'Reducing IO generic {repr(hint)}...')
        hint = reduce_hint_pep484_generic_io_to_pep544_protocol(
            hint=hint, exception_prefix=exception_prefix)
        # print(f'...{repr(hint)}.')
    # Else, this hint is either *NOT* a PEP 484-compliant IO generic base class
    # *OR* is but the active Python interpreter targets Python < 3.8 and thus
    # fails to support PEP 544-compliant protocols. In either case, preserve
    # this hint as is.

    # Return this possibly reduced hint.
    return hint
