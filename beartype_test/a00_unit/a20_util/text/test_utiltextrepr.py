#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **string munging** utility unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.text.utiltextmunge` submodule.
'''

# ....................{ IMPORTS                            }....................
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_represent_object() -> None:
    '''
    Test the :func:`beartype._util.text.utiltextrepr.represent_object`
    function.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.text.utiltextrepr import represent_object

    # ....................{ CLASSES                        }....................
    # Arbitrary class defining an unpunctuated representation (i.e.,
    # representation *NOT* already suffixed by punctuation).
    class ToASkylark(object):
        def __repr__(self):
            return 'Like a cloud of fire;'

    # Arbitrary class defining an empty representation.
    class ThouDostFloatAndRun(object):
        def __repr__(self):
            return ''

    # ....................{ LOCALS                         }....................
    # Arbitrary object whose representation is both length *AND* contains one
    # or more newlines.
    THE_EVERLASTING_UNIVERSE_OF_THINGS = (
        'And singing still dost soar,\nand soaring ever singest.')

    # ....................{ ASSERTS                        }....................
    # Assert this representer preserves the representations of terse objects
    # already suffixed by punctuation as is.
    assert represent_object(b'Higher still and higher') == repr(
        b'Higher still and higher')
    assert represent_object('From the earth thou springest') == repr(
        'From the earth thou springest')
    assert represent_object(ToASkylark) == repr(ToASkylark)

    # Assert this representer punctuates the representations of terse objects
    # *NOT* already suffixed by punctuation.
    assert represent_object(ToASkylark()) == '"Like a cloud of fire;"'

    # Assert this representer double-quotes empty representations.
    assert represent_object(ThouDostFloatAndRun()) == '""'

    # Representation of this object.
    the_blue_deep_thou_wingest = represent_object(
        obj=THE_EVERLASTING_UNIVERSE_OF_THINGS, max_len=42)

    # Assert this representer truncates this representations to that length.
    assert len(the_blue_deep_thou_wingest) == 42

    # Assert this representer removes *ALL* newlines from this representation.
    assert '\n' not in the_blue_deep_thou_wingest

    # Representation of this object, reproduced to exercise caching
    # optimizations performed within this function.
    the_pale_purple_even = represent_object(
        obj=THE_EVERLASTING_UNIVERSE_OF_THINGS, max_len=42)

    # Assert the two representations to be the same.
    assert the_blue_deep_thou_wingest == the_pale_purple_even

    # Assert this representer truncates the representations of any objects
    # exceeding an unreasonably small maximum length to that length.
    like_a_star_of_heaven = represent_object(
        obj='In the golden lightning\nOf the sunken sun,', max_len=2)
    assert len(like_a_star_of_heaven) == 2


def test_represent_func() -> None:
    '''
    Test the :func:`beartype._util.text.utiltextrepr.represent_func`
    function.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.text.utiltextrepr import represent_func
    from beartype._util.utilobject import get_object_basename_scoped
    from beartype_test.a00_unit.data.data_type import (
        function,
        function_lambda,
        function_partial,
    )

    # ....................{ ASSERTS                        }....................
    # Assert that the representation of a pure-Python non-lambda function is
    # simply its name.
    assert represent_func(function) == get_object_basename_scoped(function)

    # Assert that the representation of a pure-Python lambda function is the
    # source code for that lambda. Although we *COULD* attempt to assert the
    # actual code, doing so would be fragile across Python versions. Instead, we
    # simply assert this representation to be a non-empty string for sanity.
    function_lambda_repr = represent_func(function_lambda)
    assert isinstance(function_lambda_repr, str)
    assert function_lambda_repr

    # Assert that the representation of a pure-Python "functools.partial" object
    # is its actual repr() string.
    assert represent_func(function_partial) == repr(function_partial)


def test_represent_pith() -> None:
    '''
    Test the
    Test the :func:`beartype._util.text.utiltextrepr.represent_pith` function.
    '''

    # Defer test-specific imports.
    from beartype._util.text.utiltextrepr import represent_pith

    # Custom type to be represented below.
    class CustomType(object):
        def __repr__(self) -> str: return (
            'Collaborator‐ily brambling unspiritually')

    # Assert this representer represents builtin types in the expected way.
    repr_builtin = represent_pith(42)
    assert 'int' in repr_builtin
    assert '42' in repr_builtin

    # Assert this representer represents custom types in the expected way.
    repr_nonbuiltin = represent_pith(CustomType())
    assert 'CustomType' in repr_nonbuiltin
    assert 'Collaborator‐ily brambling unspiritually' in repr_nonbuiltin


