#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`649` **type hint utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.pep649` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ getter                     }....................
def test_get_pep649_hintable_annotations() -> None:
    '''
    Test the private
    :mod:`beartype._util.hint.pep.proposal.pep649.get_pep649_hintable_annotations`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep649Exception
    from beartype.typing import Optional
    from beartype._data.func.datafuncarg import ARG_NAME_RETURN
    from beartype._util.hint.pep.proposal.pep649 import (
        get_pep649_hintable_annotations)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_14
    from pytest import raises

    # If the active Python interpreter targets Python >= 3.14 and thus supports
    # PEP 649...
    if IS_PYTHON_AT_LEAST_3_14:
        # Defer version-specific imports.
        from beartype_test.a00_unit.data.pep.data_pep649 import (
            unit_test_get_pep649_hintable_annotations)

        # Perform this test.
        unit_test_get_pep649_hintable_annotations()
    # Else, this interpreter targets Python < 3.14 and thus fails to support PEP
    # 649.

    # ....................{ CALLABLES                      }....................
    def too_huge(for_mortal_tongue: set['MoreSorrow']) -> Optional[bytes]:
        '''
        Arbitrary callable accepting one or more parameters and returning one or
        more values -- all annotated by arbitrary type hints *not* containing
        unquoted forward references and thus supported under Python < 3.14.
        '''

        pass

    # ....................{ CLASSES                        }....................
    class MoreSorrow(object):
        '''
        Arbitrary class declaring one or more class variables annotated by
        arbitrary type hints *not* containing unquoted forward references and
        thus supported under Python < 3.14.
        '''

        like_to_this: Optional[str]
        and_such_like_woe: list['MoreSorrow']

    # ....................{ PASS                           }....................
    # Assert this getter passed an annotated callable returns the expected
    # annotations dictionary of that callable.
    assert get_pep649_hintable_annotations(too_huge) == {
        'for_mortal_tongue': set['MoreSorrow'],
        ARG_NAME_RETURN: Optional[bytes],
    }

    # Assert this getter passed an annotated class returns the expected
    # annotations dictionary of that class.
    assert get_pep649_hintable_annotations(MoreSorrow) == dict(
        like_to_this=Optional[str],
        and_such_like_woe=list['MoreSorrow'],
    )

    # ....................{ FAIL                           }....................
    # Assert this getter rejects objects that are *NOT* PEP 649-compliant
    # hintables (i.e., objects that are neither callables, modules, nor types).
    with raises(BeartypeDecorHintPep649Exception):
        get_pep649_hintable_annotations(
            'More sorrow like to this, and such like woe,')
