#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator** :pep:`613`-compliant **unit tests**.

This submodule unit tests :pep:`613` support implemented in the
:func:`beartype.beartype` decorator.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_if_python_version_less_than

# ....................{ TESTS                              }....................
@skip_if_python_version_less_than('3.10.0')
def test_decor_pep613() -> None:
    '''
    Test :pep:`613` support implemented in the :func:`beartype.beartype`
    decorator if the active Python interpreter targets Python >= 3.10 *or* skip
    otherwise.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import (
        BeartypeDecorHintPep613Exception,
        # BeartypeDecorHintPep613DeprecationWarning,
    )
    from beartype_test._util.error.pyterrraise import raises_uncached
    from typing import TypeAlias
    from warnings import simplefilter

    # ....................{ MAIN                           }....................
    # Force pytest to temporarily allow deprecation warnings to be caught by the
    # warns() context manager for the duration of this test. By default, pytest
    # simply "passes through" all deprecation warnings for subsequent reporting
    # if tests otherwise successfully pass. Deprecation warnings include:
    # * "DeprecationWarning".
    # * "FutureWarning".
    # * "PendingDeprecationWarning".
    simplefilter('always')

    # ....................{ CALLABLES                      }....................
    # Assert that the @beartype decorator raises the expected exception when
    # decorating a callable directly annotated by "typing.TypeAlias".
    with raises_uncached(BeartypeDecorHintPep613Exception):
        @beartype
        def and_shook_him() -> TypeAlias:
            '''
            Arbitrary callable directly annotated by the deprecated
            :pep:`613`-compliant :obj:`typing.TypeAlias` type hint singleton,
            which is valid *only* as a :pep:`526`-compliant annotated variable
            assignment and thus invalid as a callable parameter or return
            annotation.
            '''

            return 'And shook him from his rest, and led him forth'


    # Assert that the @beartype decorator raises the expected exception when
    # decorating a callable directly annotated by an arbitrary PEP-compliant
    # type hint factory subscripted by "typing.TypeAlias".
    with raises_uncached(BeartypeDecorHintPep613Exception):
        @beartype
        def of_our_own_valleys() -> list[TypeAlias]:
            '''
            Arbitrary callable indirectly annotated by the deprecated
            :pep:`613`-compliant :obj:`typing.TypeAlias` type hint singleton,
            which is valid *only* as a :pep:`526`-compliant annotated variable
            assignment and thus invalid as a callable parameter or return
            annotation.
            '''

            return ['Of our own valleys:', 'so I will begin',]
