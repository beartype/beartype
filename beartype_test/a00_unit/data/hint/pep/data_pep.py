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

# ....................{ IMPORTS                            }....................
from pytest import fixture

# ....................{ FIXTURES                           }....................
@fixture(scope='session')
def hints_pep_meta() -> 'Tuple[HintPepMetadata]':
    '''
    Session-scoped fixture yielding a tuple of **PEP-compliant type hint
    metadata** (i.e.,
    :class:`beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata`
    instances, each describing a sample PEP-compliant type hint exercising an
    edge case in the :mod:`beartype` codebase).

    Design
    ------
    This tuple was initially designed as a dictionary mapping from PEP-compliant
    type hints to :class:`HintPepMetadata` instances describing those hints,
    until :mod:`beartype` added support for PEPs enabling unhashable
    PEP-compliant type hints (e.g., ``collections.abc.Callable[[], str]`` under
    :pep:`585`) impermissible for use as dictionary keys or set members.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer fixture-specific imports.
    from beartype_test.a00_unit.data.hint.pep.module._data_hintmodnumpy import (
        hints_pep_meta_numpy)
    from beartype_test.a00_unit.data.hint.pep.proposal.data_pep484 import (
        hints_pep_meta_pep484)
    from beartype_test.a00_unit.data.hint.pep.proposal._data_pep544 import (
        hints_pep_meta_pep544)
    from beartype_test.a00_unit.data.hint.pep.proposal._data_pep585 import (
        hints_pep_meta_pep585)
    from beartype_test.a00_unit.data.hint.pep.proposal._data_pep586 import (
        hints_pep_meta_pep586)
    from beartype_test.a00_unit.data.hint.pep.proposal._data_pep589 import (
        hints_pep_meta_pep589)
    from beartype_test.a00_unit.data.hint.pep.proposal._data_pep593 import (
        hints_pep_meta_pep593)
    from beartype_test.a00_unit.data.hint.pep.proposal._data_pep604 import (
        hints_pep_meta_pep604)
    from beartype_test.a00_unit.data.hint.pep.proposal._data_pep675 import (
        hints_pep_meta_pep675)
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintPepMetadata)

    # ..................{ LOCALS                             }..................
    # Tuple of all fixtures defining "HINTS_PEP_META" subiterables.
    HINTS_PEP_META_FIXTURES = (
        # Standard type hints.
        hints_pep_meta_pep484,
        hints_pep_meta_pep544,
        hints_pep_meta_pep585,
        hints_pep_meta_pep586,
        hints_pep_meta_pep589,
        hints_pep_meta_pep593,
        hints_pep_meta_pep604,
        hints_pep_meta_pep675,

        # Non-standard type hints.
        hints_pep_meta_numpy,
    )

    # ..................{ LISTS                              }..................
    #FIXME: Refactor to defer to our new
    #beartype_test._util.kind.utilkindmake.make_container_from_funcs() factory!
    # List of all PEP-compliant type hint metadata to be returned.
    _hints_pep_meta = []

    # For each fixture defining a "HINTS_PEP_META" subiterable, extend the main
    # "HINTS_PEP_META" iterable by this subiterable.
    for hints_pep_meta_fixture in HINTS_PEP_META_FIXTURES:
        _hints_pep_meta.extend(hints_pep_meta_fixture())

    # Assert this global to contain only instances of its expected dataclass.
    assert (
        isinstance(hint_pep_meta, HintPepMetadata)
        for hint_pep_meta in _hints_pep_meta
    ), f'{repr(_hints_pep_meta)} not iterable of "HintPepMetadata" instances.'

    # Yield this list coerced into a tuple.
    yield tuple(_hints_pep_meta)


@fixture(scope='session')
def hints_pep_hashable(hints_pep_meta) -> frozenset:
    '''
    Session-scoped fixture yielding a frozen set of **hashable PEP-compliant
    non-class type hints** (i.e., PEP-compliant type hints that are *not*
    classes but *are* accepted by the builtin :func:`hash` function *without*
    raising an exception and thus usable in hash-based containers like
    dictionaries and sets).

    Hashable PEP-compliant class type hints (e.g., generics, protocols) are
    largely indistinguishable from PEP-noncompliant class type hints and thus
    useless for testing purposes.

    Parameters
    ----------
    hints_pep_meta : Tuple[beartype_test.a00_unit.data.hint.util.data_hintmetacls.HintPepMetadata]
        Tuple of PEP-compliant type hint metadata describing PEP-compliant type
        hints exercising edge cases in the :mod:`beartype` codebase.
    '''

    # Defer fixture-specific imports.
    from beartype._util.utilobject import is_object_hashable

    # Yield this frozen set.
    yield frozenset(
        hint_meta.hint
        for hint_meta in hints_pep_meta
        if is_object_hashable(hint_meta.hint)
    )

# ....................{ FIXTURES ~ ignorable               }....................
@fixture(scope='session')
def hints_pep_ignorable_shallow() -> frozenset:
    '''
    Session-scoped fixture yielding a frozen set of **shallowly ignorable
    PEP-compliant type hints** (i.e., ignorable on the trivial basis of their
    machine-readable representations alone and are thus in the low-level
    :obj:`beartype._data.hint.pep.datapeprepr.HINTS_REPR_IGNORABLE_SHALLOW` set,
    but which are typically *not* safely instantiable from those representations
    and thus require explicit instantiation here).
    '''

    # ..................{ IMPORTS                            }..................
    # Defer fixture-specific imports.
    from beartype_test.a00_unit.data.hint.pep.proposal.data_pep484 import (
        hints_pep484_ignorable_shallow)
    from beartype_test.a00_unit.data.hint.pep.proposal._data_pep544 import (
        hints_pep544_ignorable_shallow)

    # ..................{ LOCALS                             }..................
    # Tuple of all fixtures defining "HINTS_PEP_IGNORABLE_SHALLOW" subiterables.
    HINTS_PEP_IGNORABLE_SHALLOW_FIXTURES = (
        hints_pep484_ignorable_shallow,
        hints_pep544_ignorable_shallow,
    )

    # ..................{ LISTS                              }..................
    # List of all shallowly ignorable PEP-compliant type hints to be returned.
    from beartype.typing import Any
    _hints_pep_ignorable_shallow = [
        #FIXME: Shift into hints_pep484_ignorable_shallow(), please.

        # ..................{ PEP 484                        }..................
        # The "Any" catch-all. By definition, *ALL* objects annotated as
        # "Any" unconditionally satisfy this catch-all and thus semantically
        # reduce to unannotated objects.
        Any,

        # The root "object" superclass, which *ALL* objects annotated as
        # "object" unconditionally satisfy under isinstance()-based type
        # covariance and thus semantically reduce to unannotated objects.
        # "object" is equivalent to the "typing.Any" type hint singleton.
        object,
    ]

    #FIXME: Refactor to defer to our new
    #beartype_test._util.kind.utilkindmake.make_container_from_funcs() factory!
    # For each fixture defining a "HINTS_PEP_META" subiterable, extend the main
    # "HINTS_PEP_META" iterable by this subiterable.
    for hints_pep_ignorable_shallow_fixture in (
        HINTS_PEP_IGNORABLE_SHALLOW_FIXTURES):
        _hints_pep_ignorable_shallow.extend(
            hints_pep_ignorable_shallow_fixture())

    # Yield this list coerced into a frozen set.
    yield frozenset(_hints_pep_ignorable_shallow)


@fixture(scope='session')
def hints_pep_ignorable_deep() -> frozenset:
    '''
    Session-scoped fixture yielding a frozen set of **deeply ignorable
    PEP-compliant type hints** (i.e., *not* ignorable on the trivial basis of
    their machine-readable representations alone and are thus *not* in the
    low-level
    :obj:`beartype._data.hint.pep.datapeprepr.HINTS_REPR_IGNORABLE_DEEP` set,
    but which are nonetheless ignorable and thus require dynamic testing by the
    high-level :func:`beartype._util.hint.utilhinttest.is_hint_ignorable` tester
    function to demonstrate this fact).
    '''

    # ..................{ IMPORTS                            }..................
    # Defer fixture-specific imports.
    from beartype_test.a00_unit.data.hint.pep.proposal.data_pep484 import (
        hints_pep484_ignorable_deep)
    from beartype_test.a00_unit.data.hint.pep.proposal._data_pep544 import (
        hints_pep544_ignorable_deep)

    # ..................{ LOCALS                             }..................
    # Tuple of all fixtures defining "HINTS_PEP_IGNORABLE_DEEP" subiterables.
    HINTS_PEP_IGNORABLE_DEEP_FIXTURES = (
        hints_pep484_ignorable_deep,
        hints_pep544_ignorable_deep,
    )

    # ..................{ LISTS                              }..................
    #FIXME: Refactor to defer to our new
    #beartype_test._util.kind.utilkindmake.make_container_from_funcs() factory!
    # List of all deeply ignorable PEP-compliant type hints to be returned.
    _hints_pep_ignorable_deep = []

    # For each fixture defining a "HINTS_PEP_META" subiterable, extend the main
    # "HINTS_PEP_META" iterable by this subiterable.
    for hints_pep_ignorable_deep_fixture in (
        HINTS_PEP_IGNORABLE_DEEP_FIXTURES):
        _hints_pep_ignorable_deep.extend(
            hints_pep_ignorable_deep_fixture())

    # Yield this list coerced into a frozen set.
    yield frozenset(_hints_pep_ignorable_deep)

# ....................{ SETS                               }....................
# Initialized by the _init() function below.
HINTS_PEP_IGNORABLE_SHALLOW = {
    # ..................{ NON-PEP                            }..................
    # The root "object" superclass, which *ALL* parameters and returns annotated
    # as "object" unconditionally satisfy under isinstance()-based type
    # covariance and semantically reduce to unannotated parameters and returns.
    # "object" is thus equivalent to the "typing.Any" type hint singleton.
    object,
}
'''
Frozen set of **shallowly ignorable PEP-compliant type hints** (i.e., whose
machine-readable representations are in the low-level
:obj:`beartype._data.hint.pep.datapeprepr.HINTS_REPR_IGNORABLE_SHALLOW` set but
which are typically *not* safely instantiable from those representations and
thus require explicit instantiation here).
'''


# Initialized by the _init() function below.
HINTS_PEP_IGNORABLE_DEEP = set()
'''
Frozen set of **deeply ignorable PEP-compliant type hints** (i.e., *not* in the
low-level :data:`.HINTS_PEP_IGNORABLE_SHALLOW` set but which are nonetheless
ignorable and thus require dynamic testing by the high-level
:func:`beartype._util.hint.utilhinttest.is_hint_ignorable` tester function to
demonstrate this fact).
'''

# ....................{ INITIALIZERS                       }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    #FIXME: Excise almost everything below in favour of the standard pytest
    #fixture-based approach above, please.
    # Defer function-specific imports.
    import sys
    from beartype_test.a00_unit.data.hint.pep.proposal import (
        data_pep484,
        _data_pep544,
        _data_pep593,
        _data_pep604,
    )

    # Submodule globals to be redefined below.
    global \
        HINTS_PEP_IGNORABLE_DEEP, \
        HINTS_PEP_IGNORABLE_SHALLOW

    # Current submodule, obtained via the standard idiom. See also:
    #     https://stackoverflow.com/a/1676860/2809027
    CURRENT_SUBMODULE = sys.modules[__name__]

    # Tuple of all private submodules of this subpackage to be initialized.
    DATA_HINT_PEP_SUBMODULES = (
        data_pep484,
        _data_pep544,
        _data_pep593,
        _data_pep604,
    )

    # Initialize all private submodules of this subpackage.
    for data_hint_pep_submodule in DATA_HINT_PEP_SUBMODULES:
        data_hint_pep_submodule.add_data(CURRENT_SUBMODULE)

    # Assert these global to have been initialized by these private submodules.
    assert HINTS_PEP_IGNORABLE_DEEP, (
        'Set global "HINTS_PEP_IGNORABLE_DEEP" empty.')
    assert HINTS_PEP_IGNORABLE_SHALLOW, (
        'Set global "HINTS_PEP_IGNORABLE_SHALLOW" empty.')

    HINTS_PEP_IGNORABLE_DEEP = frozenset(HINTS_PEP_IGNORABLE_DEEP)
    HINTS_PEP_IGNORABLE_SHALLOW = frozenset(HINTS_PEP_IGNORABLE_SHALLOW)


# Initialize this submodule.
_init()
