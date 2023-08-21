#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype PEP-compliant type hints test data.**

This submodule predefines low-level global constants whose values are
PEP-compliant type hints, exercising known edge cases on behalf of higher-level
unit test submodules.
'''

# ....................{ TODO                               }....................
#FIXME: In hindsight, the structure of both this submodule and subsidiary
#submodules imported below by the _init() method is simply *ABYSMAL.* Instead:
#* Do everything below first for low-hanging fruit *NOT* widely used throughout
#  our test suite. This means (in order):
#  * "HINTS_PEP_IGNORABLE_DEEP".
#  * "HINTS_PEP_IGNORABLE_SHALLOW".
#  * "HINTS_IGNORABLE".
#  * "HINTS_PEP_HASHABLE".
#  * "NOT_HINTS_NONPEP".
#  * "HINTS_PEP_META".
#
#  In particular, avoid attempting to refactor "HINTS_PEP_META" until *AFTER*
#  refactoring everything else. Refactoring "HINTS_PEP_META" will prove
#  extremely time-consuming and thus non-trivial, sadly. *sigh*
#* Define one new @pytest.fixture-decorated session-scoped function for each
#  public global variable currently defined below: e.g.,
#      # Instead of this...
#      HINTS_PEP_IGNORABLE_SHALLOW = None
#
#      # ...do this instead.
#      from beartype_test.a00_util.data.hint.pep.proposal.data_pep484 import (
#          hints_pep_ignorable_shallow_pep484,
#      )
#      from beartype_test.a00_util.data.hint.pep.proposal._data_pep593 import (
#          hints_pep_ignorable_shallow_pep593,
#      )
#      from collections.abc import Set
#      from pytest import fixture
#
#      @fixture(scope='session')
#      def hints_pep_ignorable_shallow(
#          hints_pep_ignorable_shallow_pep484,
#          hints_pep_ignorable_shallow_pep593,
#          ...,
#      ) -> Set:
#          return (
#              hints_pep_ignorable_shallow_pep484 |
#              hints_pep_ignorable_shallow_pep593 |
#              ...
#          )
#* In the "beartype_test.a00_unit.conftest" submodule, import those fixtures to
#  implicitly expose those fixtures to all unit tests: e.g.,
#      from beartype_test.a00_util.data.hint.pep.data_pep import (
#          hints_pep_ignorable_shallow,
#      )
## Refactor all unit tests previously explicitly importing
#  "HINTS_PEP_IGNORABLE_SHALLOW" to instead accept the
#  "hints_pep_ignorable_shallow" fixture as a function parameter: e.g.,
#      def test_em_up(hints_pep_ignorable_shallow: Set) -> None: ...
#
#The advantages are obvious. Currently, we unconditionally build these globals
#out in an extremely convoluted process that happens really extremely early at
#*PYTEST COLLECTION TIME.* That's horrible. The above refactoring instead defers
#that build-out to *TEST CALL TIME.* Any tests skipped or ignored for the
#current test session will result in fixtures required by those tests also being
#skipped and ignored. Ultimately, though, the principal benefit is
#maintainability; the above approach isolates PEP-specific data containers to
#their own PEP-specific fixtures, which are then composable into even larger
#PEP-agnostic fixtures. It just makes sense. Let's do this sometime, everybody.

# ....................{ SETS                               }....................
# Initialized by the _init() function below.
HINTS_PEP_HASHABLE = None
'''
Frozen set of **hashable PEP-compliant non-class type hints** (i.e.,
PEP-compliant type hints that are *not* classes but *are* accepted by the
builtin :func:`hash` function *without* raising an exception and thus usable in
hash-based containers like dictionaries and sets).

Hashable PEP-compliant class type hints (e.g., generics, protocols) are largely
indistinguishable from PEP-noncompliant class type hints and thus useless for
testing purposes.
'''


# Initialized by the _init() function below.
HINTS_PEP_IGNORABLE_SHALLOW = {
    # ..................{ NON-PEP                            }..................
    # The PEP-noncompliant builtin "object" type is the transitive superclass
    # of all classes, parameters and return values annotated as "object"
    # unconditionally match *ALL* objects under isinstance()-based type
    # covariance and thus semantically reduce to unannotated parameters and
    # return values. This is literally the "beartype.cave.AnyType" type.
    object,
}
'''
Frozen set of **shallowly ignorable PEP-compliant type hints** (i.e.,
PEP-compliant type hints that are shallowly ignorable and whose
machine-readable representations are in the low-level
:attr:`beartype._data.hint.pep.datapeprepr.HINTS_REPR_IGNORABLE_SHALLOW`
set, but which are typically *not* safely instantiable from those
representations and thus require explicit instantiation here).
'''


# Initialized by the _init() function below.
HINTS_PEP_IGNORABLE_DEEP = set()
'''
Frozen set of **deeply ignorable PEP-compliant type hints** (i.e.,
PEP-compliant type hints that are *not* shallowly ignorable and thus *not* in
the low-level :data:`HINTS_PEP_IGNORABLE_SHALLOW` set, but which are
nonetheless ignorable and thus require dynamic testing by the high-level
:func:`beartype._util.hint.utilhinttest.is_hint_ignorable` tester function to
demonstrate this fact).
'''

# ....................{ TUPLES                             }....................
# Initialized by the _init() function below.
HINTS_PEP_META = []
'''
Tuple of **PEP-compliant type hint metadata** (i.e., :class:`HintPepMetadata`
instances describing test-specific PEP-compliant type hints with metadata
leveraged by various testing scenarios).

Design
----------
This tuple was initially designed as a dictionary mapping from PEP-compliant
type hints to :class:`HintPepMetadata` instances describing those hints, until
:mod:`beartype` added support for PEPs enabling unhashable PEP-compliant type
hints (e.g., ``collections.abc.Callable[[], str]`` under :pep:`585`)
impermissible for use as dictionary keys or set members.
'''

# ....................{ INITIALIZERS                       }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # Defer function-specific imports.
    import sys
    from beartype._util.utilobject import is_object_hashable
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintPepMetadata)
    from beartype_test.a00_unit.data.hint.pep.module import (
        _data_hintmodnumpy)
    from beartype_test.a00_unit.data.hint.pep.proposal import (
        data_pep484,
        _data_pep544,
        _data_pep585,
        _data_pep586,
        _data_pep589,
        _data_pep593,
        _data_pep604,
        _data_pep675,
    )

    # Submodule globals to be redefined below.
    global \
        HINTS_PEP_HASHABLE, \
        HINTS_PEP_IGNORABLE_DEEP, \
        HINTS_PEP_IGNORABLE_SHALLOW, \
        HINTS_PEP_META

    # Current submodule, obtained via the standard idiom. See also:
    #     https://stackoverflow.com/a/1676860/2809027
    CURRENT_SUBMODULE = sys.modules[__name__]

    # Tuple of all private submodules of this subpackage to be initialized.
    DATA_HINT_PEP_SUBMODULES = (
        _data_hintmodnumpy,
        data_pep484,
        _data_pep544,
        _data_pep585,
        _data_pep586,
        _data_pep589,
        _data_pep593,
        _data_pep604,
        _data_pep675,
    )

    # Initialize all private submodules of this subpackage.
    for data_hint_pep_submodule in DATA_HINT_PEP_SUBMODULES:
        data_hint_pep_submodule.add_data(CURRENT_SUBMODULE)

    # Assert these global to have been initialized by these private submodules.
    assert HINTS_PEP_IGNORABLE_DEEP, (
        'Set global "HINTS_PEP_IGNORABLE_DEEP" empty.')
    assert HINTS_PEP_IGNORABLE_SHALLOW, (
        'Set global "HINTS_PEP_IGNORABLE_SHALLOW" empty.')
    assert HINTS_PEP_META, 'Tuple global "HINTS_PEP_META" empty.'

    # Assert this global to contain only instances of its expected dataclass.
    assert (
        isinstance(hint_pep_meta, HintPepMetadata)
        for hint_pep_meta in HINTS_PEP_META
    ), f'{repr(HINTS_PEP_META)} not iterable of "HintPepMetadata" instances.'

    # Frozen sets defined *AFTER* initializing these private submodules and
    # thus the lower-level globals required by these sets.
    HINTS_PEP_HASHABLE = frozenset(
        hint_pep_meta.hint
        for hint_pep_meta in HINTS_PEP_META
        if is_object_hashable(hint_pep_meta.hint)
    )
    HINTS_PEP_IGNORABLE_DEEP = frozenset(HINTS_PEP_IGNORABLE_DEEP)
    HINTS_PEP_IGNORABLE_SHALLOW = frozenset(HINTS_PEP_IGNORABLE_SHALLOW)
    HINTS_PEP_META = tuple(HINTS_PEP_META)


# Initialize this submodule.
_init()
