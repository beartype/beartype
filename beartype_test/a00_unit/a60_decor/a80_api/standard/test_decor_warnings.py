#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype decorator :mod:`warnings`-specific unit tests.

This submodule unit tests the :func:`beartype.beartype` decorator with respect
the standard :mod:`warnings` module.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_if_python_version_less_than

# ....................{ TESTS                              }....................
@skip_if_python_version_less_than('3.13.0')
def test_decor_warnings_deprecated() -> None:
    '''
    Test the :func:`beartype.beartype` decorator on
    :func:`warnings.contextmanager`-decorated **synchronous context managers**
    (i.e., generator factory functions decorated by that standard decorator) if
    the active Python interpreter targets Python >= 3.13 and thus supports
    :pep:`702` *or* silently reduce to a noop otherwise.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from beartype._util.module.utilmodimport import import_module_or_none
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_13
    from collections.abc import Generator
    from contextlib import contextmanager
    from pytest import (
        raises,
        warns,
    )
    from warnings import simplefilter, deprecated

    # ....................{ MAIN                           }....................
    # Force pytest to temporarily allow deprecation warnings to be caught by the
    # warns() context manager for the duration of this test. By default, pytest
    # simply "passes through" all deprecation warnings for subsequent reporting
    # if tests otherwise successfully pass. Deprecation warnings include:
    # * "DeprecationWarning".
    # * "FutureWarning".
    # * "PendingDeprecationWarning".
    simplefilter('always')

    # ....................{ EXCEPTIONS                     }....................
    class AndRebellion(DeprecationWarning):
        '''
        Arbitrary non-builtin deprecation warning.
        '''

        pass

    # ....................{ CALLABLES                      }....................
    @beartype
    @deprecated(
        'Of these, thy brethren and the Goddesses!',
        # Intentionally pass a non-default warning category to test edge cases!
        category=AndRebellion,
    )
    @contextmanager
    def thy_brethren(and_the_goddesses: str) -> Generator[str, None, None]:
        '''
        Arbitrary context manager decorated in the non-ideal order by
        :func:`beartype.beartype`, :class:`warnings.deprecated`, *and*
        :func:`contextlib.contextmanager`.
        '''

        yield and_the_goddesses

    # ....................{ PASS                           }....................
    # Assert that the non-ideal context manager when passed a valid parameter
    # issues a non-fatal deprecation warning of this non-defaut category
    # *AND*...
    with warns(AndRebellion):
        # Yields the expected value.
        with thy_brethren('There is sad feud among ye, and rebellion') as of_these:
            assert of_these == 'There is sad feud among ye, and rebellion'

    # ....................{ FAIL                           }....................
    # Assert that the non-ideal context manager when passed an invalid parameter
    # issues a non-fatal deprecation warning of this non-defaut category
    # *AND*...
    with warns(AndRebellion):
        with raises(BeartypeCallHintParamViolation):
            with thy_brethren(b'There is sad feud among ye, and rebellion'):
                pass
