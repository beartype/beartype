#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **type hint ignorers** (i.e., low-level callables detecting whether
type hints are ignorable or not).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype._check.convert._ignore._ignmap import (
    HINT_SIGN_TO_IS_HINT_IGNORABLE_get)
from beartype._check.metadata.metasane import (
    HintOrHintSanifiedData,
    get_hint_or_sane_hint,
)
from beartype._data.hint.pep.datapeprepr import HINTS_REPR_IGNORABLE_SHALLOW
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.hint.pep.utilpepget import get_hint_pep_sign
from beartype._util.hint.pep.utilpeptest import is_hint_pep
from beartype._util.hint.utilhintget import get_hint_repr
# from beartype._util.module.utilmodtest import (
#     is_object_module_thirdparty_blacklisted)

# ....................{ TESTERS                            }....................
@callable_cached
def is_hint_ignorable(hint_or_sane: HintOrHintSanifiedData) -> bool:
    '''
    :data:`True` only if the passed type hint is **ignorable** (i.e., conveys
    *no* meaningful semantics despite superficially appearing to do so).

    This tester is memoized for efficiency.

    Caveats
    -------
    **The higher-level**
    :func:`beartype._check.convert.convsanify.sanify_hint_if_unignorable_or_none`
    **function should always be called in lieu of this lower-level function.**
    Whereas the former reduces this possibly insane hint to a sane hint *before*
    testing whether that sane hint is ignorable, the latter fails to perform
    that reduction and thus returns a false negative when the passed hint is
    insane (i.e., has yet to be reduced to a sane hint).

    Parameters
    ----------
    hint_or_sane : HintOrHintSanifiedData
        Either a type hint *or* **sanified type hint metadata** (i.e.,
        :data:`.HintSanifiedData` object) to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this type hint is ignorable.
    '''

    # Hint encapsulated by this metadata.
    hint = get_hint_or_sane_hint(hint_or_sane)

    # Machine-readable representation of this hint.
    hint_repr = get_hint_repr(hint)

    #FIXME: Preserved for posterity, as this seems generically useful. *sigh*
    # # If this hint is beartype-blacklisted (i.e., defined in a third-party
    # # package or module that is hostile to runtime type-checking), return true.
    # # print(f'Testing hint {repr(hint)} third-party blacklisting...')
    # if is_object_module_thirdparty_blacklisted(hint):
    #     # print('Blacklisted!')
    #     return True
    # # Else, this hint is *NOT* beartype-blacklisted.

    # True only if this hint is ignorable, defined as either...
    #
    # Note that this iteratively tests this hint for ignorability against a
    # battery of increasingly non-trivial tests. For efficiency, tests are
    # intentionally ordered from most to least efficient.
    is_ignorable: bool = (
        # This hint is shallowly ignorable *OR*...
        hint_repr in HINTS_REPR_IGNORABLE_SHALLOW or
        # Else, this hint is *NOT* shallowly ignorable.
        #
        # This hint is both...
        (
            # A PEP-compliant hint *AND*...
            is_hint_pep(hint) and
            # Deeply ignorable as such.
            _is_hint_pep_ignorable(hint_or_sane)
        )
    )

    # Return true only if this hint is ignorable.
    return is_ignorable

# ....................{ PRIVATE ~ testers                  }....................
def _is_hint_pep_ignorable(hint_or_sane: HintOrHintSanifiedData) -> bool:
    '''
    :data:`True` only if the passed PEP-compliant type hint is **deeply
    ignorable** (i.e., shown to be ignorable only after recursively inspecting
    the contents of this hint).

    This tester is intentionally *not* memoized (e.g., by the
    :func:`beartype._util.cache.utilcachecall.callable_cached` decorator), as
    This tester is only safely callable by the memoized parent
    :func:`beartype._util.hint.utilhinttest.is_hint_ignorable` tester.

    Parameters
    ----------
    hint_or_sane : HintOrHintSanifiedData
        Either a PEP-compliant type hint *or* **sanified PEP-compliant type hint
        metadata** (i.e., :data:`.HintSanifiedData` object) to be inspected.

    Returns
    -------
    bool
        :data:`True` only if this PEP-compliant type hint is deeply ignorable.

    Warns
    -----
    BeartypeDecorHintPepIgnorableDeepWarning
        If this object is a deeply ignorable PEP-compliant type hint. Why?
        Because deeply ignorable PEP-compliant type hints convey *no*
        meaningful semantics but superficially appear to do so. Consider
        ``Union[str, List[int], NewType('MetaType', Annotated[object, 53])]``,
        for example; this PEP-compliant type hint effectively reduces to
        :obj:`typing.Any` and thus conveys *no* meaningful semantics despite
        superficially appearing to do so.
    '''

    # print(f'Testing PEP hint {repr(hint)} deep ignorability...')

    # Hint encapsulated by this metadata.
    hint = get_hint_or_sane_hint(hint_or_sane)

    # Sign uniquely identifying this hint.
    hint_sign = get_hint_pep_sign(hint)

    # Ignorer (i.e., callable testing whether this hint is ignorable) if an
    # ignorer for hints of this sign is defined *OR* "None" otherwise (i.e.,
    # if *NO* such ignorer is defined, in which case this hint is unignorable).
    is_ignorable_tester = HINT_SIGN_TO_IS_HINT_IGNORABLE_get(hint_sign)

    # True only if this hint is ignorable, defined as...
    is_ignorable: bool = (
        # An ignorer for hints of this sign is defined *AND*...
        is_ignorable_tester is not None and
        # This ignorer detects this hint as deeply ignorable.
        is_ignorable_tester(hint_or_sane)
    )
    # print(f'[ignorable] hint: {repr(hint)}; tester: {repr(is_hint_ignorer)}')
    # print(f'[ignorable] is_ignorable: {repr(is_ignorable)}')

    # Return true only if this hint is ignorable.
    return is_ignorable
