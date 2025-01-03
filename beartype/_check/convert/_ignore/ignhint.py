#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **type hint ignorers** (i.e., low-level callables detecting whether
type hints are ignorable or not).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ TODO                               }....................
#FIXME: *LOL.* In hindsight, this entire subpackage can be (more or less)
#trivially refactored away. How? First, consider that reductions are now largely
#the fundamental type-checking operation performed at decoration time. Next,
#consider that *ANY* ignorable hint can simply be ignored via by:
#* Refactoring the corresponding is_hint_pep*_ignorable() tester into a new
#  reduce_hint_pep*() reducer such that that reducer returns the "typing.Any"
#  singleton when passed that ignorable hint.
#
#Trivial. The idea here is that we just reduce *DEEPLY* ignorable hints like
#"int | Any" to *SHALLOWLY* ignorable hints like "Any". Once we've done that,
#the only functionality required for detecting ignorable hints would be the
#trivial "hint_repr in HINTS_REPR_IGNORABLE_SHALLOW" check in the existing
#is_hint_ignorable() tester defined below. That check would detect "typing.Any"
#and "object" as shallowly ignorable.
#
#Refactoring ignorable testers into reducers now makes fundamental sense,
#because reductions *MUST* be performed anyway before testing ignorability.
#Ergo, we'd might as well simply remove the middle-man (i.e., ignorable testers)
#and just do reductions for literally everything.
#
#The following would then be trivially removable:
#* The _is_hint_pep_ignorable() tester defined below.
#* The entire "_ignmap" submodule here.
#* The entire "_pep" subpackage here.
#
#That said, time is growing short for the @beartype 0.20.0 release cycle. Let's
#temporarily hold off on this obvious improvement until @beartype 0.20.1,
#please. *sigh*

# ....................{ IMPORTS                            }....................
from beartype._check.metadata.metasane import (
    HintOrHintSanifiedData,
    get_hint_or_sane_hint,
)
from beartype._data.hint.pep.datapeprepr import HINTS_REPR_IGNORABLE_SHALLOW
from beartype._util.hint.utilhintget import get_hint_repr
# from beartype._util.module.utilmodtest import (
#     is_object_module_thirdparty_blacklisted)

# ....................{ TESTERS                            }....................
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

    #FIXME: Refactor this into a new trivial reducer, please. Let's a-go!
    # True only if this hint is shallowly ignorable.
    #
    # Note that this iteratively tests this hint for ignorability against a
    # battery of increasingly non-trivial tests. For efficiency, tests are
    # intentionally ordered from most to least efficient.
    is_ignorable = hint_repr in HINTS_REPR_IGNORABLE_SHALLOW

    # Return true only if this hint is ignorable.
    return is_ignorable
