#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
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
    PEP-compliant type hints (e.g., ``typing.Annotated[list, []]`` under
    :pep:`593`) impermissible for use as dictionary keys or set members.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer fixture-specific imports.
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_12
    from beartype_test.a00_unit.data.hint.util.data_hintmetacls import (
        HintPepMetadata)
    from beartype_test._util.kind.pytkindmake import make_container_from_funcs

    # ..................{ LIST                               }..................
    _hints_pep_meta = make_container_from_funcs((
        # PEP-compliant type hints.
        'beartype_test.a00_unit.data.hint.pep.proposal.data_pep484.hints_pep484_meta',
        'beartype_test.a00_unit.data.hint.pep.proposal._data_pep544.hints_pep544_meta',
        'beartype_test.a00_unit.data.hint.pep.proposal._data_pep585.hints_pep585_meta',
        'beartype_test.a00_unit.data.hint.pep.proposal._data_pep586.hints_pep586_meta',
        'beartype_test.a00_unit.data.hint.pep.proposal._data_pep589.hints_pep589_meta',
        'beartype_test.a00_unit.data.hint.pep.proposal._data_pep593.hints_pep593_meta',
        'beartype_test.a00_unit.data.hint.pep.proposal._data_pep604.hints_pep604_meta',
        'beartype_test.a00_unit.data.hint.pep.proposal._data_pep675.hints_pep675_meta',

        # PEP-noncompliant type hints defined by both standard and third-party
        # packages internally treated by @beartype as PEP-compliant to
        # streamline code generation.
        #
        # PEP-noncompliant type hints are intentionally tested *AFTER*
        # PEP-compliant type hints to simplify debugging in the event that core
        # functionality is catastrophically broken. *gulp*
        'beartype_test.a00_unit.data.hint.pep.module._data_hintmodnumpy.hints_pep_meta_numpy',
        'beartype_test.a00_unit.data.hint.pep.module._data_hintmodos.hints_pep_meta_os',
        'beartype_test.a00_unit.data.hint.pep.module._data_hintmodweakref.hints_pep_meta_weakref',
    ))

    # If the active Python interpreter targets Python >= 3.12, this interpreter
    # supports PEP 695 -- including the PEP 695-specific "type" alias statement
    # whose syntax is *EXTREMELY* invalid under prior Python versions. Ideally,
    # this syntax would simply be ignored by older Python versions like all
    # other PEP-specific syntax developed by newer Python versions (e.g., PEP
    # 604-style "|"-delimited new unions). Sadly, older Python versions raise
    # exceptions resembling the following on attempting to import from *ANY*
    # modules containing even a single PEP 695-specific "type" alias statement
    # -- even if those older Python versions never even execute that statement:
    #     SyntaxError: invalid syntax  # <-- uhh, wut
    if IS_PYTHON_AT_LEAST_3_12:
        from beartype_test.a00_unit.data.hint.pep.proposal._data_pep695 import (
            hints_pep695_meta)
        _hints_pep_meta.extend(hints_pep695_meta())
    # Else, the active Python interpreter targets Python < 3.12 and thus fails
    # to support PEP 695.

    # ..................{ YIELD                              }..................
    # Assert this list contains *ONLY* instances of the expected dataclass.
    assert (
        isinstance(hint_pep_meta, HintPepMetadata)
        for hint_pep_meta in _hints_pep_meta
    ), f'{repr(_hints_pep_meta)} not iterable of "HintPepMetadata" instances.'

    # Yield a tuple coerced from this list.
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
    machine-readable representations alone and thus in the low-level
    :obj:`beartype._data.hint.pep.datapeprepr.HINTS_REPR_IGNORABLE_SHALLOW` set,
    but which are typically *not* safely instantiable from those representations
    and thus require explicit instantiation here).
    '''

    # ..................{ IMPORTS                            }..................
    # Defer fixture-specific imports.
    from beartype_test._util.kind.pytkindmake import make_container_from_funcs

    # ..................{ FIXTURE                            }..................
    # List of all shallowly ignorable PEP-compliant type hints to be returned.
    _hints_pep_ignorable_shallow = make_container_from_funcs((
        'beartype_test.a00_unit.data.hint.pep.proposal.data_pep484.hints_pep484_ignorable_shallow',
        'beartype_test.a00_unit.data.hint.pep.proposal._data_pep544.hints_pep544_ignorable_shallow',
    ))

    # Yield a frozen set coerced from this list.
    yield frozenset(_hints_pep_ignorable_shallow)


@fixture(scope='session')
def hints_pep_ignorable_deep() -> frozenset:
    '''
    Session-scoped fixture yielding a frozen set of **deeply ignorable
    PEP-compliant type hints** (i.e., *not* ignorable on the trivial basis of
    their machine-readable representations alone and thus *not* in the low-level
    :obj:`beartype._data.hint.pep.datapeprepr.HINTS_REPR_IGNORABLE_DEEP` set,
    but which are nonetheless ignorable and thus require dynamic testing by the
    high-level :func:`beartype._util.hint.utilhinttest.is_hint_ignorable` tester
    function to demonstrate this fact).
    '''

    # ..................{ IMPORTS                            }..................
    # Defer fixture-specific imports.
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_12
    from beartype_test._util.kind.pytkindmake import make_container_from_funcs

    # ..................{ FIXTURE                            }..................
    # List of all deeply ignorable PEP-compliant type hints to be returned.
    _hints_pep_ignorable_deep = make_container_from_funcs((
        'beartype_test.a00_unit.data.hint.pep.proposal.data_pep484.hints_pep484_ignorable_deep',
        'beartype_test.a00_unit.data.hint.pep.proposal._data_pep544.hints_pep544_ignorable_deep',
        'beartype_test.a00_unit.data.hint.pep.proposal._data_pep593.hints_pep593_ignorable_deep',
        'beartype_test.a00_unit.data.hint.pep.proposal._data_pep604.hints_pep604_ignorable_deep',
    ))

    # If the active Python interpreter targets Python >= 3.12, this interpreter
    # supports PEP 695 -- including the PEP 695-specific "type" alias statement
    # whose syntax is *EXTREMELY* invalid under prior Python versions. Ideally,
    # this syntax would simply be ignored by older Python versions like all
    # other PEP-specific syntax developed by newer Python versions (e.g., PEP
    # 604-style "|"-delimited new unions). Sadly, older Python versions raise
    # exceptions resembling the following on attempting to import from *ANY*
    # modules containing even a single PEP 695-specific "type" alias statement
    # -- even if those older Python versions never even execute that statement:
    #     SyntaxError: invalid syntax  # <-- uhh, wut
    if IS_PYTHON_AT_LEAST_3_12:
        from beartype_test.a00_unit.data.hint.pep.proposal._data_pep695 import (
            hints_pep695_ignorable_deep)
        _hints_pep_ignorable_deep.extend(hints_pep695_ignorable_deep())
    # Else, the active Python interpreter targets Python < 3.12 and thus fails
    # to support PEP 695.

    # Yield a frozen set coerced from this list.
    yield frozenset(_hints_pep_ignorable_deep)
