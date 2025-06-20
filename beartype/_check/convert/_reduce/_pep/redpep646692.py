#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`646`- and :pep:`692`-compliant **unpack reducers** (i.e.,
low-level callables converting ``typing.Unpack[...]`` type hints subscripted by
either :pep:`646`-compliant type variable tuples *or* :pep:`692`-compliant
:class:`typing.TypedDict` subclasses to lower-level type hints more readily
consumable by :mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: [PEP 692] Actually implement deep type-checking support for PEP
#692-compliant unpack type hints of the form "**kwargs:
#typing.Unpack[UserTypedDict]". Doing so will *ALMOST CERTAINLY* necessitate a
#new logic pathway for dynamically generating type-checking code efficiently
#type-checking the passed variadic keyword argument dictionary "**kwargs"
#against that user-defined "UserTypedDict". Feasible, but non-trivial. *sigh*

# ....................{ IMPORTS                            }....................
from beartype.roar import (
    BeartypeDecorHintPep646Exception,
    BeartypeDecorHintPep692Exception,
)
from beartype.typing import Optional
from beartype._data.hint.datahintpep import Hint
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignTypedDict,
    HintSignTypeVarTuple,
)
from beartype._util.func.arg.utilfuncargiter import ArgKind
from beartype._util.hint.pep.utilpepget import get_hint_pep_args
from beartype._util.hint.pep.utilpepsign import get_hint_pep_sign_or_none

# ....................{ REDUCERS                           }....................
#FIXME: Unit test us up, including:
#* Unsubscripted "typing.Unpack" type hints, which should be unconditionally
#  *PROHIBITED.* They signify nothing. "typing.Unpack" should *ALWAYS* be
#  subscripted by at least something.
def reduce_hint_pep646692_unpack(
    hint: Hint,
    arg_kind: Optional[ArgKind],
    exception_prefix: str,
    **kwargs
) -> Hint:
    '''
    Reduce the passed :pep:`646`- or :pep:`692`-compliant **unpack hint** (i.e.,
    ``typing.Unpack[...]`` type hint subscripted by either a
    :pep:`646`-compliant type variable tuple *or* :pep:`589`-compliant
    :class:`typing.TypedDict` subclass) to a more readily digestible hint.

    Specifically, if the passed hint is:

    * A :pep:`646`-compliant unpack type hint subscripted by a
      :pep:`646`-compliant type variable tuple, this reducer effectively ignores
      this hint by reduction to the ignorable :class:`object` superclass (e.g.,
      from ``typing.Unpack[Ts]`` to simply ``object``). Although non-ideal,
      generating code type-checking these hints is sufficiently non-trivial to
      warrant a (hopefully) temporary delay in doing so properly. Note that:

      * Python itself unconditionally expands every unpacking of a
        :pep:`646`-compliant type variable tuple to this form of a
        :pep:`646`-compliant unpack type hint (e.g., from ``*Ts`` to
        ``typing.Unpack[Ts]``).
      * As a consequence of the prior note, :pep:`646`-compliant unpack type
        hints are as common as unpackings of :pep:`646`-compliant type variable
        tuples -- which is to say, increasingly common.

    * A :pep:`692`-compliant unpack type hint subscripted by a
      :pep:`589`-compliant :class:`typing.TypedDict` subclass, this reducer
      effectively ignores this hint by reduction to the ignorable
      :class:`object` superclass (e.g., from ``**kwargs:
      typing.Unpack[UserTypedDict]`` to simply ``**kwargs``). Although
      non-ideal, generating code type-checking these hints is sufficiently
      non-trivial to warrant a (hopefully) temporary delay in doing so properly.

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as reducers cannot be memoized.

    Parameters
    ----------
    hint : Hint
        :pep:`646`- or :pep:`692`-compliant unpack type hint to be reduced.
    arg_kind : Optional[ArgKind]
        Either:

        * If this hint annotates a parameter of some callable, that parameter's
          **kind** (i.e., :class:`.ArgKind` enumeration member conveying the
          syntactic class of that parameter, constraining how the callable
          declaring that parameter requires that parameter to be passed).
        * Else, :data:`None`.
    exception_prefix : str
        Human-readable substring prefixing raised exception messages.

    All remaining keyword-only parameters are silently ignored.

    Returns
    -------
    Hint
        Lower-level type hint currently supported by :mod:`beartype`.

    Raises
    ------
    BeartypeDecorHintPep646Exception
        If this hint does *not* annotate a variadic keyword parameter and is
        *not* subscripted by a single :pep:`646`-compliant type variable tuple.
    BeartypeDecorHintPep692Exception
        If this hint annotates a variadic keyword parameter but is *not*
        subscripted by a single :pep:`589`-compliant :class:`typing.TypedDict`
        subclass.
    '''

    # ....................{ LOCALS                         }....................
    # Tuple of the single child hint subscripting this parent unpack hint. Note
    # that the "typing.Unpack" type hint factory has already pre-validated this
    # factory to accept at most one child type hint:
    #     >>> from typing import Unpack
    #     >>> Unpack['shaking', 'my', 'head']
    #     TypeError: typing.Unpack accepts only single type. Got ('shaking',
    #     'my', 'head').
    hint_childs = get_hint_pep_args(hint)

    # Child hint subscripting this parent unpack hint.
    hint_child = hint_childs[0]

    # Sign uniquely identifying this child hint if any *OR* "None".
    hint_child_sign = get_hint_pep_sign_or_none(hint_child)

    # ....................{ PEP 692                        }....................
    # Validate the passed variadic positional or keyword parameter type hint.

    # If this hint directly annotates a variadic keyword parameter, this is a
    # PEP 692- rather than 646-compliant hint. In this case...
    if arg_kind is ArgKind.VARIADIC_KEYWORD:
        # If this child hint is *NOT* a PEP 589-compliant "typing.TypeDict"
        # subclass, raise an exception.
        if hint_child_sign is not HintSignTypedDict:
            raise BeartypeDecorHintPep692Exception(
                f'{exception_prefix}PEP 692 unpack type hint {repr(hint)} '
                f'child type hint {repr(hint_child)} not '
                f'PEP 589 "typing.TypeDict" subclass.'
            )
        # Else, this child hint is a PEP 589-compliant "typing.TypeDict"
        # subclass.

        # Silently reduce to a noop by returning the ignorable "object"
        # superclass. While non-ideal, worky is preferable to non-worky.
        return object
    # Else, this hint does *NOT* directly annotate a variadic keyword parameter,
    # implying this is a PEP 646-compliant hint.

    # ....................{ PEP 646                        }....................
    # If this child hint is *NOT* a PEP 646-compliant "typing.TypeVarTuple"
    # object, raise an exception.
    if hint_child_sign is not HintSignTypeVarTuple:
        raise BeartypeDecorHintPep646Exception(
            f'{exception_prefix}PEP 646 unpack type hint {repr(hint)} '
            f'child type hint {repr(hint_child)} not '
            f'PEP 646 type variable tuple '
            f'(i.e., "typing.TypeVarTuple" object).'
        )
    # Else, this child hint is a PEP 646-compliant "typing.TypeVarTuple" object.

    # Silently reduce to a noop by returning the ignorable "object" superclass.
    # While non-ideal, worky is preferable to non-worky.
    return object
