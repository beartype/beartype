#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`-compliant **reducers** (i.e., low-level callables
converting :pep:`484`-compliant type hints to lower-level type hints more
readily consumable by :mod:`beartype`).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.meta import URL_PEP585_DEPRECATIONS
from beartype.roar import BeartypeDecorHintPep585DeprecationWarning
from beartype._cave._cavefast import NoneType
from beartype._check.metadata.hint.hintsane import (
    HINT_SANE_IGNORABLE,
    HintSane,
)
from beartype._data.hint.datahintrepr import (
    HINTS_PEP484_REPR_PREFIX_DEPRECATED)
from beartype._data.typing.datatyping import TypeStack
from beartype._data.typing.datatypingport import Hint
from beartype._util.error.utilerrwarn import issue_warning

# ....................{ REDUCERS ~ deprecated              }....................
def reduce_hint_pep484_deprecated(
    hint: Hint, exception_prefix: str, **kwargs) -> Hint:
    '''
    Preserve the passed :pep:`484`-compliant hint as is while conditionally
    emitting a non-fatal deprecation warning if this hint is deprecated (e.g.,
    due to having been obsoleted by an equivalent :pep:`585`-compliant hint).

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as doing so would prevent this reducer from
    emitting one warning per deprecated hint.

    Parameters
    ----------
    hint : Hint
        Type hint to be reduced.
    exception_prefix : str
        Human-readable substring prefixing emitted warning messages.

    All remaining passed arguments are silently ignored.

    Returns
    -------
    Hint
        This hint unmodified.

    Warns
    -----
    BeartypeDecorHintPep585DeprecationWarning
        If this is a :pep:`484`-compliant type hint deprecated by :pep:`585`.
    '''
    # print(f'Testing PEP 484 type hint {repr(hint)} for PEP 585 deprecation...')
    # print(f'{HINTS_PEP484_REPR_PREFIX_DEPRECATED}')

    # Avoid circular import dependencies.
    from beartype._util.hint.utilhintget import get_hint_repr

    # Machine-readable representation of this hint.
    hint_repr = get_hint_repr(hint)

    # Substring of the machine-readable representation of this hint preceding
    # the first "[" delimiter if this representation contains that delimiter
    # *OR* this representation as is otherwise.
    #
    # Note that the str.partition() method has been profiled to be the optimally
    # efficient means of parsing trivial prefixes.
    hint_repr_bare = hint_repr.partition('[')[0]

    # If this hint is a PEP 484-compliant type hint originating from an origin
    # type (e.g., "typing.List[int]"), this hint has been deprecated by the
    # equivalent PEP 585-compliant type hint (e.g., "list[int]"). In this
    # case...
    if hint_repr_bare in HINTS_PEP484_REPR_PREFIX_DEPRECATED:
        assert isinstance(exception_prefix, str), (
            f'{repr(exception_prefix)} not string.')

        # Emit a non-fatal PEP 585-specific deprecation warning.
        issue_warning(
            cls=BeartypeDecorHintPep585DeprecationWarning,
            message=(
                f'{exception_prefix}PEP 484 type hint {repr(hint)} '
                f'deprecated by PEP 585. '
                f'This hint is scheduled for removal in the first Python '
                f'version released after October 5th, 2025. To resolve this, '
                f'import this hint from "beartype.typing" rather than "typing". '
                f'For further commentary and alternatives, see also:\n'
                f'    {URL_PEP585_DEPRECATIONS}'
            ),
        )
    # Else, this hint is *NOT* deprecated. In this case, reduce to a noop.

    # Preserve this hint as is, regardless of deprecation.
    return hint

# ....................{ REDUCERS ~ forwardref              }....................
#FIXME: Add to the "_redmap" submodule, please.
#FIXME: Unit test us up, please.
#FIXME: Finalize implementation, please. Useful reductions for this reducer to
#eventually perform include:
#* Of a relative unqualified forward reference referring to a non-nested class
#  to that class if the "cls_stack" contains *ONLY* that class.
#* Of a relative qualified forward reference referring to a nested class to that
#  class if the "cls_stack" contains two or more classes.
#* Of an absolute unqualified forward reference referring to a builtin type.
#  Pretty sure we have similar functionality elsewhere. Our PEP 563 resolver,
#  perhaps? *shrug*
#* Of a relative unqualified forward reference referring to a *GLOBAL* attribute
#  of the module defining this *METHOD* if this reduction is being performed
#  against a *METHOD*, as is the case when the "cls_stack" parameter is
#  non-"None". In this case, we can trivially obtain these globals with a
#  similar one-liner to that suggested by PEP 563 (lol):
#      cls_globals = vars(sys.modules[cls_stack[-1].__module__])
#
#  Of course, note that "__module__" may be either "None" *OR* an imaginary
#  in-memory string that has no relation to "sys.modules". Some care is thus
#  warranted.
#
#  Note that the above one-liner should be expanded into a more general-purpose
#  get_type_globals() getter. We currently define get_type_locals() but *NOT*
#  get_type_globals(), interestingly. *shrug*
#* Of a relative unqualified forward reference referring to a *CLASS* attribute
#  of the type currently being decorated. Note that all class attributes are
#  efficiently accessible via the existing get_type_locals() getter. Call it!
#* Of a relative forward reference referring to a *GLOBAL* attribute of the
#  module defining this callable if this reduction is being performed against a
#  callable, as is the case when the "decor_meta" parameter is non-"None".
#  Recall that "decor_meta.func_wrappee_wrappee.__globals__" efficiently
#  provides the dictionary mapping from the names to values of all global
#  attributes accessible to the unwrapped decorated callable.
#
#  Note that:
#  * We intentionally do *NOT* bother attempting to resolve relative forward
#    reference referring to a *LOCAL*, as resolving local attributes against an
#    arbitrary callable is extremely inefficient in the general case.
#  * This reduction is currently pointless to attempt, despite being both
#    intelligent and useful. Why? Because higher-level callers calling the
#    parent reduce_hint() function currently *ONLY* pass the requisite
#    "decor_meta" parameter when the root type hint is being sanified by the
#    sanify_hint_root_func() sanifier. Two refactorings thus need to happen to
#    make this proposed reduction here useful:
#    * But a totally different code path in the coerce_func_hint_root() function
#      already reduces root type hints that are forward references! Ideally, the
#      coerce_func_hint_root() function should stop performing that reduction.
#    * Other sanifiers need to both receive and pass "decor_meta". The issue
#      is... maybe it's not even feasible! In all likelihood, "decor_meta" isn't
#      even accessible in those lower-level contexts, because that would destroy
#      memoization.
#  * In other words, this is probably impossible. Oh, well.
#
#Initially focus *ONLY* on the "cls_stack" use case, please. Those are the ones
#we absolutely *MUST* implement. They're *NOT* optimizations; they're critical
#reductions supporting edge-case type hints that *CANNOT* be readily supported
#any other way. The remainder of the above reductions are merely optimizations
#(albeit useful optimizations at that).
def reduce_hint_pep484_ref(
    hint: Hint,
    cls_stack: TypeStack,
    **kwargs
) -> Hint:
    '''
    Reduce the passed :pep:`484`-compliant **forward reference hint** (i.e.,
    object indirectly referring to a user-defined type that typically has yet to
    be defined) to the object this reference refers to if that object is
    efficiently accessible at this early decoration time *or* preserve this
    reference as is otherwise.

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), due to requiring contextual parameters and
    thus being fundamentally unmemoizable.

    Parameters
    ----------
    hint : Hint
        Type hint to be reduced.
    cls_stack : TypeStack
        **Type stack** (i.e., either a tuple of the one or more
        :func:`beartype.beartype`-decorated classes lexically containing the
        class variable or method annotated by this hint *or* :data:`None`).

    All remaining passed arguments are silently ignored.

    Returns
    -------
    Hint
        Either:

        * If the object this hint refers to is efficiently accessible at this
          early decoration time, that object.
        * Else, this hint unmodified.
    '''

    #FIXME: Do something like the following, please.
    #
    #Note that the higher-level get_hint_pep484_ref_names_relative_to() getter
    #is *NOT* safely callable in this context, as this context cannot guarantee
    #that both the "cls_stack" *AND* "func" parameters are non-"None", in which
    #case that getter *COULD* raise an undesirable exception.

    # # Possibly undefined fully-qualified module name and possibly unqualified
    # # classname referred to by this forward reference.
    # hint_module_name, hint_ref_name = get_hint_pep484_ref_names(
    #     hint=hint,
    #     exception_cls=exception_cls,
    #     exception_prefix=exception_prefix,
    # )

    # Return this forward reference unmodified as a fallback.
    return hint

# ....................{ REDUCERS ~ singleton               }....................
def reduce_hint_pep484_any(hint: Hint, exception_prefix: str) -> HintSane:
    '''
    Reduce the passed :pep:`484`-compliant :obj:`typing.Any` singleton to the
    ignorable :data:`.HINT_SANE_IGNORABLE` singleton.

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : Hint
        :obj:`typing.Any` hint to be reduced.
    exception_prefix : str
        Human-readable substring prefixing raised exception messages.

    Returns
    -------
    HintSane
        Ignorable :data:`.HINT_SANE_IGNORABLE` singleton.
    '''

    # Unconditionally ignore the "Any" singleton.
    return HINT_SANE_IGNORABLE


# Note that this reducer is intentionally typed as returning "type" rather than
# "NoneType". While the former would certainly be preferable, mypy erroneously
# emits false positives when this reducer is typed as returning "NoneType":
#     beartype._util.hint.pep.proposal.pep484.pep484.py:190: error: Variable
#     "beartype._cave._cavefast.NoneType" is not valid as a type [valid-type]
def reduce_hint_pep484_none(hint: Hint, exception_prefix: str) -> type:
    '''
    Reduce the passed :pep:`484`-compliant :data:`None` singleton to the type of
    :data:`None` (i.e., the builtin :class:`types.NoneType` class).

    While *not* explicitly defined by the :mod:`typing` module, :pep:`484`
    explicitly supports this singleton:

        When used in a type hint, the expression :data:`None` is considered
        equivalent to ``type(None)``.

    This reducer is intentionally *not* memoized (e.g., by the
    ``callable_cached`` decorator), as the implementation trivially reduces
    to an efficient one-liner.

    Parameters
    ----------
    hint : Hint
        :data:`None` hint to be reduced.
    exception_prefix : str
        Human-readable substring prefixing raised exception messages.

    Returns
    -------
    type[NoneType]
        Type of the :data:`None` singleton.
    '''
    assert hint is None, f'Type hint {hint} not "None" singleton.'

    # Unconditionally return the type of the "None" singleton.
    return NoneType
