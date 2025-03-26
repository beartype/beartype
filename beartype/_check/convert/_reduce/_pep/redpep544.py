#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`544`-compliant **type alias reducers** (i.e., low-level
callables converting higher-level objects created via the ``type`` statement
under Python >= 3.12 to lower-level type hints more readily consumable by
:mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeDecorHintPep544Exception
from beartype._check.metadata.hint.hintsane import (
    HINT_IGNORABLE,
    HintOrSane,
)
from beartype._data.api.standard.datamodtyping import TYPING_MODULE_NAMES
from beartype._data.hint.datahintpep import Hint
from beartype._util.hint.pep.proposal.pep544 import (
    HINT_PEP484_IO_GENERIC_TO_PEP544_PROTOCOL,
    make_HINT_PEP484_IO_GENERIC_TO_PEP544_PROTOCOL,
    is_hint_pep484_generic_io,
)
from beartype._util.hint.pep.utilpepget import (
    get_hint_pep_origin_or_none,
    get_hint_pep_typevars,
)
from beartype._util.hint.utilhintget import get_hint_repr

# ....................{ REDUCERS                           }....................
def reduce_hint_pep544(hint: Hint, exception_prefix: str, **kwargs) -> (
    HintOrSane):
    '''
    Reduce the passed :pep:`544`-compliant **protocol** (i.e., user-defined
    subclass of the :class:`typing.Protocol` abstract base class (ABC)) to the
    ignorable :data:`.HINT_IGNORABLE` singleton if this protocol is a
    parametrization of this ABC by one or more :pep:`484`-compliant **type
    variables** (i.e., :class:`typing.TypeVar` objects).

    As the name implies, this ABC is generic and thus fails to impose any
    meaningful constraints. Since a type variable in and of itself also fails to
    impose any meaningful constraints, these parametrizations are safely
    ignorable in all possible runtime contexts: e.g.,

    .. code-block:: python

       from typing import Protocol, TypeVar
       T = TypeVar('T')
       def noop(param_hint_ignorable: Protocol[T]) -> T: pass

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as reducers cannot be memoized.

    Parameters
    ----------
    hint : Hint
        Type hint to be reduced.
    exception_prefix : str
        Human-readable substring prefixing raised exception messages.

    All remaining passed keyword parameters are silently ignored.

    Returns
    -------
    HintOrSane
        Lower-level type hint currently supported by :mod:`beartype`.
    '''

    #FIXME: *SUPER-WEIRD.* This logic is totally cray-cray. What the heck is
    #this O(n) search madness? This is why we have signs, people. So that we
    #don't have to manually crawl over "TYPING_MODULE_NAMES". In theory, the
    #same exact test should trivially reduce to:
    #    if (
    #        hint.__name__ == 'Protocol' and
    #        hint.__module__ in TYPING_MODULE_NAMES
    #    ):
    #        return HINT_IGNORABLE
    #FIXME: Actually, the "redpep484585generic" submodule has ever simpler logic
    #that we should pilfer from:
    #    # If this subscripted generic is the "typing.Protocol" superclass directly
    #    # parametrized by one or more type variables (e.g., "typing.Protocol[T]"),
    #    # this generic is ignorable. In this case, reduce this ignorable generic to
    #    # the ignorable singleton.
    #    #
    #    # Note that we intentionally avoid calling the
    #    # get_hint_pep_origin_type_isinstanceable_or_none() function here, which has
    #    # been intentionally designed to exclude PEP-compliant type hints
    #    # originating from "typing" type origins for stability reasons.
    #    if get_hint_pep_origin_or_none(hint) is Protocol:
    #        return HINT_IGNORABLE
    #
    #We facepalm. We facepalm so hard.

    # Machine-readable representation of this hint.
    hint_repr = get_hint_repr(hint)

    # If this representation contains a relevant substring suggesting that this
    # hint *MIGHT* be the "Protocol" superclass directly parametrized by type
    # variables (e.g., "typing.Protocol[S, T]")...
    if 'Protocol[' in hint_repr:
        # For the fully-qualified name of each typing module...
        for typing_module_name in TYPING_MODULE_NAMES:
            # If this hint is the "Protocol" superclass defined by this module
            # directly parametrized by one or more type variables (e.g.,
            # "typing.Protocol[S, T]"), ignore this superclass by returning the
            # ignorable "HINT_IGNORABLE" singleton. This superclass can *ONLY*
            # be parametrized by type variables; a string test thus suffices.
            #
            # For unknown and uninteresting reasons, *ALL* possible objects
            # satisfy the "Protocol" superclass. Ergo, this superclass and *ALL*
            # parametrizations of this superclass are synonymous with the
            # "object" root superclass.
            if hint_repr.startswith(f'{typing_module_name}.Protocol['):
                return HINT_IGNORABLE
            # Else, this hint is *NOT* such a "Protocol" superclass. In this
            # case, continue to the next typing module.
        # Else, this hint is *NOT* the "Protocol" superclass directly
        # parametrized by one or more type variables.
    # Else, this representation contains such *NO* such substring.

    # Return this protocol unmodified, as *ALL* other "Protocol" subclasses are
    # unignorable by definition.
    return hint


def reduce_hint_pep484_generic_io_to_pep544_protocol(
    hint: Hint, exception_prefix: str) -> Hint:
    '''
    :pep:`544`-compliant :mod:`beartype` **IO protocol** (i.e., either
    :class:`._Pep544IO` itself *or* a subclass of that class defined by this
    submodule intentionally designed to be usable at runtime) corresponding to
    the passed :pep:`484`-compliant :mod:`typing` **IO generic base class**
    (i.e., either :class:`typing.IO` itself *or* a subclass of
    :class:`typing.IO` defined by the :mod:`typing` module effectively unusable
    at runtime due to botched implementation details).

    This reducer is intentionally *not* memoized (e.g., by the
    :func:`callable_cached` decorator), as the implementation trivially reduces
    to an efficient one-liner thanks to caching internally performed by this
    reducer.

    Parameters
    ----------
    hint : Hint
        :pep:`484`-compliant :mod:`typing` IO generic base class to be replaced
        by the corresponding :pep:`544`-compliant :mod:`beartype` IO protocol.
    exception_prefix : str
        Human-readable label prefixing the representation of this object in the
        exception message.

    Returns
    -------
    Protocol
        :pep:`544`-compliant :mod:`beartype` IO protocol corresponding to this
        :pep:`484`-compliant :mod:`typing` IO generic base class.

    Raises
    ------
    BeartypeDecorHintPep544Exception
        If this object is *not* a :pep:`484`-compliant IO generic base class.
    '''

    # If this object is *NOT* a PEP 484-compliant "typing" IO generic,
    # raise an exception.
    if not is_hint_pep484_generic_io(hint):
        raise BeartypeDecorHintPep544Exception(
            f'{exception_prefix}type hint {repr(hint)} not '
            f'PEP 484 IO generic base class '
            f'(i.e., "typing.IO", "typing.BinaryIO", or "typing.TextIO").'
        )
    # Else, this object is *NOT* a PEP 484-compliant "typing" IO generic.
    #
    # If this dictionary has yet to be initialized, this submodule has yet to be
    # initialized. In this case, do so.
    #
    # Note that this initialization is intentionally deferred until required.
    # Why? Because this initialization performs somewhat space- and
    # time-intensive work -- including importation of the "beartype.vale"
    # subpackage, which we strictly prohibit importing from global scope.
    elif not HINT_PEP484_IO_GENERIC_TO_PEP544_PROTOCOL:
        make_HINT_PEP484_IO_GENERIC_TO_PEP544_PROTOCOL()
    # In any case, this dictionary is now initialized.

    # PEP 544-compliant IO protocol implementing this PEP 484-compliant IO
    # generic if any *OR* "None" otherwise.
    pep544_protocol = HINT_PEP484_IO_GENERIC_TO_PEP544_PROTOCOL.get(hint)

    # If *NO* PEP 544-compliant IO protocol implements this generic...
    if pep544_protocol is None:
        # Tuple of zero or more type variables parametrizing this hint.
        hint_typevars = get_hint_pep_typevars(hint)

        #FIXME: Unit test us up, please.
        # If this hint is unparametrized, raise an exception.
        if not hint_typevars:
            raise BeartypeDecorHintPep544Exception(
                f'{exception_prefix}PEP 484 IO generic base class '
                f'{repr(hint)} invalid (i.e., not subscripted (indexed) by '
                f'either "str", "bytes", "typing.Any", or "typing.AnyStr").'
            )
        # Else, this hint is parametrized and thus defines the "__origin__"
        # dunder attribute whose value is the type originating this hint.

        #FIXME: Attempt to actually handle this type variable, please.
        # Reduce this parametrized hint (e.g., "typing.IO[typing.AnyStr]") to
        # the equivalent unparametrized hint (e.g., "typing.IO"), effectively
        # ignoring the type variable parametrizing this hint.
        hint_unparametrized: type = get_hint_pep_origin_or_none(hint)  # type: ignore[assignment]

        # PEP 544-compliant IO protocol implementing this unparametrized PEP
        # 484-compliant IO generic. For efficiency, we additionally cache this
        # mapping under the original parametrized hint to minimize the cost of
        # similar reductions under subsequent annotations.
        pep544_protocol = \
            HINT_PEP484_IO_GENERIC_TO_PEP544_PROTOCOL[hint] = \
            HINT_PEP484_IO_GENERIC_TO_PEP544_PROTOCOL[hint_unparametrized]
    # Else, some PEP 544-compliant IO protocol implements this generic.

    # Return this protocol.
    return pep544_protocol
