#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype decorator :mod:`contextlib`-specific unit tests.

This submodule unit tests the :func:`beartype.beartype` decorator with respect
the standard :mod:`contextlib` module.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_if_python_version_less_than

# ....................{ TESTS                              }....................
@skip_if_python_version_less_than('3.11.0')
def test_decor_contextlib_contextmanager() -> None:
    '''
    Test the :func:`beartype.beartype` decorator on
    :func:`contextlib.contextmanager`-based **context managers** (i.e.,
    generator factory functions decorated by that standard decorator) if the
    active Python interpreter targets Python >= 3.11 and thus defines the
    ``co_qualname`` attribute on code objects required to implement this
    functionality *or* skip this test otherwise.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from beartype.typing import (
        Iterator,
        Union,
    )
    from contextlib import contextmanager
    from pytest import raises

    # ....................{ CONTEXTS                       }....................
    @contextmanager
    @beartype
    def and_motions_of(
        the_forests_and_the_sea: Union[int, float]) -> Iterator[int]:
        '''
        Arbitrary :func:`contextlib.contextmanager`-decorated context manager
        decorated by :func:`beartype.beartype` in the ideal order.
        '''

        yield int(the_forests_and_the_sea)


    @beartype
    @contextmanager
    def may_modulate_with(
        murmurs_of_the_air: str) -> Iterator[Union[str, bool]]:
        '''
        Arbitrary :func:`contextlib.contextmanager`-decorated context manager
        decorated by :func:`beartype.beartype` in a non-ideal order.
        '''

        yield murmurs_of_the_air

    # ....................{ PASS                           }....................
    # Assert that the ideal context manager when passed a valid parameter
    # returns the expected return.
    with and_motions_of(len(
        'Of night and day, and the deep heart of man.')) as (
        deep_heart_of_man):
        assert deep_heart_of_man == len(
            'Of night and day, and the deep heart of man.')

    # Assert that the non-ideal context manager when passed a valid parameter
    # returns the expected return.
    with may_modulate_with(
        'And voice of living beings, and woven hymns') as and_woven_hymns:
        assert and_woven_hymns == 'And voice of living beings, and woven hymns'

    # ....................{ FAIL                           }....................
    # Assert that the ideal context manager when passed an invalid parameter
    # raises the expected exception.
    with raises(BeartypeCallHintParamViolation):
        and_motions_of('No human hands with pious reverence reared,')

    # Assert that the non-ideal context manager when passed an invalid parameter
    # raises the expected exception.
    with raises(BeartypeCallHintParamViolation):
        may_modulate_with(b'There was a Poet whose untimely tomb')
