#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`484`- and :pep:`604`-compliant **union type hint utility**
unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.pep484604` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ tester                     }....................
def test_is_hint_pep604() -> None:
    '''
    Test the private
    :mod:`beartype._util.hint.pep.proposal.pep484604.is_hint_pep604` tester.
    '''

    # Defer test-specific imports.
    from beartype._util.hint.pep.proposal.pep484604 import is_hint_pep604
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_10

    # If the active Python interpreter targets Python >= 3.10 and thus supports
    # PEP 604...
    if IS_PYTHON_AT_LEAST_3_10:
        # Assert this tester accepts a PEP 604-compliant union.
        assert is_hint_pep604(int | str | None) is True
    # Else, this interpreter targets Python < 3.10 and thus fails to support PEP
    # 604.

    # Assert this tester rejects an arbitrary PEP 604-noncompliant object.
    is_hint_pep604('Meet in the vale, and one majestic River,')

# ....................{ TESTS ~ factory                    }....................
def test_make_hint_pep484604_union() -> None:
    '''
    Test the private
    :mod:`beartype._util.hint.pep.proposal.pep484604.make_hint_pep484604_union`
    factory.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep604Exception
    from beartype.typing import (
        List,
        Union,
    )
    from beartype._util.hint.pep.proposal.pep484604 import (
        make_hint_pep484604_union)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_10
    from pytest import raises

    # ....................{ PASS                           }....................
    # Assert that this factory when passed a 1-tuple containing an arbitrary
    # child type hint simply returns that hint as is.
    assert make_hint_pep484604_union((int,)) is int

    # Assert that this factory when passed a tuple containing two or more PEP
    # 604-compliant child type hints returns either...
    assert make_hint_pep484604_union((int, List[str], None)) == (
        # If the active Python interpreter targets Python >= 3.10 and thus
        # supports PEP 604, a PEP 604-compliant new-style union of these hints;
        int | List[str] | None
        if IS_PYTHON_AT_LEAST_3_10 else
        # Else, the active Python interpreter targets Python < 3.10 and thus
        # fails to support PEP 604. In this case, a PEP 484-compliant old-style
        # union of these hints.
        Union[int, List[str], None]
    )

    # If the active Python interpreter targets Python >= 3.10 and thus supports
    # both PEP 593 (i.e., "typing.Annotated[...]" type hints) *AND* 604...
    if IS_PYTHON_AT_LEAST_3_10:
        # Defer version-specific imports.
        from beartype.typing import Annotated

        # Assert that this factory when passed a tuple containing two or more
        # child type hints at least one of which is PEP 593-compliant and thus
        # *NOT* PEP 604-compliant returns a PEP 484-compliant old-style union of
        # these hints.
        assert make_hint_pep484604_union(
            (bool, List[int], None, Annotated[bytes, None])) == Union[
             bool, List[int], None, Annotated[bytes, None]]
    # Else, the active Python interpreter targets Python < 3.10 and thus fails
    # to support at least PEP 604. In this case, don't even bother. Run away!

    # ....................{ FAIL                           }....................
    # Assert that this factory raises the expected exception when passed the
    # empty tuple.
    with raises(BeartypeDecorHintPep604Exception):
        make_hint_pep484604_union(())
