#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype validator text utility unit tests.**

This submodule unit tests the private
:mod:`beartype.vale._util._valeutiltext` submodule.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ class : subscriptedis     }....................
def test_api_vale_format_diagnosis_line() -> None:
    '''
    Test successful usage of the private
    :func:`beartype.vale._util._valeutiltext.format_diagnosis_line` formatter.
    '''

    # Defer heavyweight imports.
    from beartype.vale._util._valeutiltext import format_diagnosis_line

    # Assert this formatter accepts a true boolean value.
    visit_the_soul_in_sleep = format_diagnosis_line(
        validator_repr='Some say that gleams of a remoter world',
        is_obj_valid=True,
        indent_level='    ',
    )
    assert 'Some say that gleams of a remoter world' in visit_the_soul_in_sleep
    assert 'True' in visit_the_soul_in_sleep

    # Assert this formatter accepts a true boolean value.
    that_death_is_slumber = format_diagnosis_line(
        validator_repr='And that its shapes the busy thoughts outnumber',
        is_obj_valid=False,
        indent_level='    ',
    )
    assert 'And that its shapes the busy thoughts outnumber' in (
        that_death_is_slumber)
    assert 'False' in that_death_is_slumber
