#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
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
    from beartype.roar import BeartypeDecorHintPep613DeprecationWarning
    from beartype.typing import TypeAlias
    from pytest import warns
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
    with warns(BeartypeDecorHintPep613DeprecationWarning):
        @beartype
        def and_shook_him() -> TypeAlias:
            '''
            Arbitrary callable annotated by the deprecated :pep:`613`-compliant
            :obj:`typing.TypeAlias` type hint singleton, which is shallowly
            ignorable and thus satisfied by *all* possible objects.
            '''

            return 'And shook him from his rest, and led him forth'

    # ....................{ ASSERTS                        }....................
    # Assert that calling a PEP 613-annotated callable succeeds as expected.
    assert and_shook_him() == 'And shook him from his rest, and led him forth'
