#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype configuration unit tests.**

This submodule unit tests the subset of the public API of the :mod:`beartype`
package defined by the private :mod:`beartype._conf.confenum` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_conf_enum_decoration_position() -> None:
    '''
    Test the public :func:`beartype.BeartypeDecorationPosition` enumeration.
    '''

    # Defer test-specific imports.
    from beartype import BeartypeDecorationPosition

    # Assert this enumeration declares the expected members.
    assert isinstance(
        BeartypeDecorationPosition.FIRST, BeartypeDecorationPosition)
    assert isinstance(
        BeartypeDecorationPosition.LAST, BeartypeDecorationPosition)


def test_conf_enum_strategy() -> None:
    '''
    Test the public :func:`beartype.BeartypeStrategy` enumeration.
    '''

    # Defer test-specific imports.
    from beartype import BeartypeStrategy

    # Assert this enumeration declares the expected members.
    assert isinstance(BeartypeStrategy.O0, BeartypeStrategy)
    assert isinstance(BeartypeStrategy.O1, BeartypeStrategy)
    assert isinstance(BeartypeStrategy.Ologn, BeartypeStrategy)
    assert isinstance(BeartypeStrategy.On, BeartypeStrategy)


def test_conf_enum_violation_verbosity() -> None:
    '''
    Test the public :func:`beartype.BeartypeViolationVerbosity` enumeration.
    '''

    # Defer test-specific imports.
    from beartype import BeartypeViolationVerbosity

    # Assert this enumeration declares the expected members.
    assert isinstance(BeartypeViolationVerbosity.MINIMAL, int)
    assert isinstance(BeartypeViolationVerbosity.DEFAULT, int)
    assert isinstance(BeartypeViolationVerbosity.MAXIMAL, int)
