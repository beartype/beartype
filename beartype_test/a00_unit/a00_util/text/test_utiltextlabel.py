#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
# See "LICENSE" for further details.

"""
**Beartype object label utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.text.utiltextmunge.py` submodule.
"""


# ....................{ IMPORTS                           }....................
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                             }....................
def test_label_callable():
    '''
    Test the :func:`beartype._util.text.utiltextlabel.prefix_callable`
    function.
    '''

    # Defer heavyweight imports.
    from beartype._util.text.utiltextlabel import prefix_callable

    # Arbitrary lambda function declared on-disk.
    ozymandias = lambda: 'I met a traveller from an antique land,'

    # Arbitrary lambda function declared in-memory.
    which_yet_survive = eval("lambda: 'stamped on these lifeless things'")

    # Arbitrary non-lambda function declared on-disk.
    def half_sunk_a_shattered_visage_lies_whose_frown():
        return 'And wrinkled lip, and sneer of cold command,'

    # Assert this labeller labels an on-disk lambda.
    two_vast_and_trunkless_legs_of_stone = prefix_callable(ozymandias)
    assert isinstance(two_vast_and_trunkless_legs_of_stone, str)
    assert bool(two_vast_and_trunkless_legs_of_stone)

    # Assert this labeller labels an in-memory lambda.
    the_hand_that_mocked_them = prefix_callable(which_yet_survive)
    assert isinstance(the_hand_that_mocked_them, str)
    assert bool(the_hand_that_mocked_them)

    # Assert this labeller labels an on-disk non-lambda with the name of that
    # non-lambda.
    tell_that_its_sculptor_well_those_passions_read = prefix_callable(
        half_sunk_a_shattered_visage_lies_whose_frown)
    assert isinstance(tell_that_its_sculptor_well_those_passions_read, str)
    assert half_sunk_a_shattered_visage_lies_whose_frown.__name__ in (
        tell_that_its_sculptor_well_those_passions_read)
