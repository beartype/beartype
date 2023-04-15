#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

"""
**Beartype object label utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.text.utiltextlabel` submodule.
"""


# ....................{ IMPORTS                            }....................
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_label_beartypeable_kind() -> None:
    '''
    Test the :func:`beartype._util.text.utiltextlabel.label_beartypeable_kind`
    function.
    '''

    # Defer test-specific imports.
    from beartype._util.text.utiltextlabel import label_beartypeable_kind
    from beartype_test.a00_unit.data.data_type import (
        CallableClass,
        Class,
        function,
    )

    # Tuple of 2-tuples "(beartypeable, cls_stack, kind)", where:
    # * "beartypeable" is an input object to be passed to this labeller.
    # * "cls_stack" is the input class stack lexically declaring this input
    #   object if any *OR* "None" otherwise to also be passed to this labeller.
    # * "kind" is the string expected to be returned from this labeller when
    #   passed this input object.
    BEARTYPEABLES_KINDS = (
        # Builtin type.
        (str, None, 'class'),

        # User-defined class.
        (Class, None, 'class'),

        # Pure-Python function.
        (function, None, 'function'),

        # Pure-Python method.
        (Class.instance_method, Class, 'method'),

        # Object that is neither a pure-Python class, function, *NOR* method. In
        # this case, pass a pseudo-callable (i.e., object whose class defines
        # the __call__() dunder method) to exercise a *POSSIBLE* edge case.
        (CallableClass(), None, 'object'),
    )

    # For each such input object, class stack, and expected string...
    for beartypeable, cls_stack, kind in BEARTYPEABLES_KINDS:
        # Assert this labeller returns the expected string when passed this
        # input object.
        assert label_beartypeable_kind(beartypeable, cls_stack) == kind


def test_label_callable() -> None:
    '''
    Test the :func:`beartype._util.text.utiltextlabel.label_callable`
    function.
    '''

    # Defer test-specific imports.
    from beartype._util.text.utiltextlabel import label_callable
    from beartype_test.a00_unit.data.data_type import (
        async_coroutine_factory,
        async_generator_factory,
        sync_generator_factory,
    )
    from beartype_test.a00_unit.data.util.mod.data_utilmodule_line import (
        like_snakes_that_watch_their_prey,
        ozymandias,
        which_yet_survive,
    )

    # Assert this labeller labels an on-disk lambda function as expected.
    two_vast_and_trunkless_legs_of_stone = label_callable(ozymandias)
    assert isinstance(two_vast_and_trunkless_legs_of_stone, str)
    assert 'lambda' in two_vast_and_trunkless_legs_of_stone

    # Assert this labeller labels an in-memory lambda function as expected.
    the_hand_that_mocked_them = label_callable(which_yet_survive)
    assert isinstance(the_hand_that_mocked_them, str)
    assert 'lambda' in the_hand_that_mocked_them

    # Assert this labeller labels an on-disk non-lambda callable as expected.
    tell_that_its_sculptor_well_those_passions_read = label_callable(
        like_snakes_that_watch_their_prey)
    assert isinstance(tell_that_its_sculptor_well_those_passions_read, str)
    assert like_snakes_that_watch_their_prey.__name__ in (
        tell_that_its_sculptor_well_those_passions_read)

    # Assert this labeller labels an on-disk coroutine as expected.
    async_coroutine_label = label_callable(async_coroutine_factory)
    assert isinstance(async_coroutine_label, str)
    assert async_coroutine_factory.__name__ in async_coroutine_label
    assert 'coroutine' in async_coroutine_label

    # Assert this labeller labels an on-disk asynchronous generator as expected.
    async_generator_label = label_callable(async_generator_factory)
    assert isinstance(async_generator_label, str)
    assert async_generator_factory.__name__ in async_generator_label
    assert 'asynchronous generator' in async_generator_label

    # Assert this labeller labels an on-disk synchronous generator as expected.
    sync_generator_label = label_callable(sync_generator_factory)
    assert isinstance(sync_generator_label, str)
    assert sync_generator_factory.__name__ in sync_generator_label
    assert 'generator' in sync_generator_label


def test_label_type() -> None:
    '''
    Test the :func:`beartype._util.text.utiltextlabel.label_type`
    function.
    '''

    # Defer test-specific imports.
    from beartype._util.text.utiltextlabel import label_type
    from beartype_test.a00_unit.data.data_type import Class

    # Assert this labeller returns the expected label for a builtin type.
    assert label_type(str) == 'str'

    # Assert this labeller returns the expected label for the non-builtin type
    # of the "None" singleton, exercising a common edge case.
    assert label_type(type(None)) == '<class "builtins.NoneType">'

    # Assert this labeller returns the expected label for a user-defined type.
    assert label_type(Class) == (
        '<class "beartype_test.a00_unit.data.data_type.Class">')
