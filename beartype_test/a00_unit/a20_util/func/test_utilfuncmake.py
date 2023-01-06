#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Callable creation utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.utilfunc.utilfuncmake` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ GLOBALS                            }....................
# Arbitrary global referenced in functions created below.
AND_SEE_THE_GREAT_ACHILLES = 'whom we knew'

# ....................{ TESTS ~ make                       }....................
#FIXME: Consider excising. Although awesome, this is no longer needed.
# def test_copy_func_shallow_pass() -> None:
#     '''
#     Test successful usage of the
#     :func:`beartype._util.func.utilfuncmake.copy_func_shallow` function.
#     '''
#
#     # Defer test-specific imports.
#     from beartype.roar import BeartypeDecorWrapperException
#     from beartype._util.func.utilfuncmake import copy_func_shallow
#
#     # Tuple of the names of all attributes expected to be shallowly copied.
#     ATTRS_NAME_COPIED = (
#         '__annotations__',
#         '__closure__',
#         '__code__',
#         '__defaults__',
#         '__doc__',
#         '__globals__',
#         # '__kwdefaults__',
#         '__module__',
#         '__name__',
#         '__qualname__',
#     )
#
#     # String returned by the in_memoriam() function declared below when passed
#     # an even integer.
#     IN_MEMORIAM_RETURN_IF_PARAM_EVEN = 'And all we met was fair and good,'
#
#     # String returned by the in_memoriam() function declared below when passed
#     # an even integer.
#     IN_MEMORIAM_RETURN_IF_PARAM_ODD = '   And all was good that Time could bring,'
#
#     # String suffixing the string returned by that function.
#     IN_MEMORIAM_RETURN_SUFFIX = 'I sing to him that rests below,'
#
#     # Arbitrary closure to be shallowly copied.
#     def in_memoriam(
#         # Mandatory parameter.
#         the_shadow: int,
#
#         # Optional parameter.
#         the_shroud: str = IN_MEMORIAM_RETURN_SUFFIX,
#     ) -> str:
#         '''
#         The Shadow sits and waits for me.
#         '''
#
#         return (
#             IN_MEMORIAM_RETURN_IF_PARAM_EVEN + the_shroud
#             if the_shadow % 2 == 0 else
#             IN_MEMORIAM_RETURN_IF_PARAM_ODD + the_shroud
#         )
#
#     # Set a custom attribute on this callable to be shallowly copied.
#     in_memoriam.the_clock = '''
#        And in the dusk of thee, the clock
#     Beats out the little lives of men.'''
#
#     # Function shallowly copied from this callable.
#     captive_void = copy_func_shallow(func=in_memoriam)
#
#     # Assert this copy returns the expected value.
#     assert captive_void(27) == (
#         f'{IN_MEMORIAM_RETURN_IF_PARAM_ODD}{IN_MEMORIAM_RETURN_SUFFIX}')
#
#     # Assert this copy shares the same custom attribute as the original.
#     assert captive_void.the_clock == in_memoriam.the_clock
#
#     # Assert this copy contains the same dunder attributes.
#     for attr_name_copied in ATTRS_NAME_COPIED:
#         assert (
#             getattr(captive_void, attr_name_copied) ==
#             getattr(in_memoriam,  attr_name_copied)
#         )
#
#     # Assert this function rejects C-based functions.
#     with raises(BeartypeDecorWrapperException):
#         copy_func_shallow(
#             func=iter, exception_cls=BeartypeDecorWrapperException)

# ....................{ TESTS ~ make                       }....................
def test_make_func_pass(capsys) -> None:
    '''
    Test successful usage of the
    :func:`beartype._util.func.utilfuncmake.make_func` function.

    Parameters
    ----------
    capsys
        :mod:`pytest` fixture enabling standard output and error to be reliably
        captured and tested against from within unit tests and fixtures.

    Parameters
    ----------
    https://docs.pytest.org/en/latest/how-to/capture-stdout-stderr.html#accessing-captured-output-from-a-test-function
        Official ``capsys`` reference documentation.
    '''

    # Defer test-specific imports.
    from beartype._util.func.utilfuncmake import make_func
    from beartype.typing import Optional
    from linecache import cache as linecache_cache

    # Arbitrary local referenced in functions created below.
    THO_MUCH_IS_TAKEN = 'much abides; and tho’'

    # Arbitrary callable wrapped by wrappers created below.
    def we_are_not_now_that_strength_which_in_old_days() -> str:
        '''
        One equal temper of heroic hearts,
        '''

        return 'Moved earth and heaven, that which we are, we are;'

    # Arbitrary wrapper accessing both globally and locally scoped attributes,
    # exercising most optional parameters.
    ulysses = make_func(
        func_name='it_may_be_that_the_gulfs_will_wash_us_down',
        func_code='''
def it_may_be_that_the_gulfs_will_wash_us_down(
    it_may_be_we_shall_touch_the_happy_isles: Optional[str]) -> str:
    return (
        AND_SEE_THE_GREAT_ACHILLES +
        THO_MUCH_IS_TAKEN +
        we_are_not_now_that_strength_which_in_old_days() +
        (
            it_may_be_we_shall_touch_the_happy_isles or
            'Made weak by time and fate, but strong in will'
        )
    )
''',
        func_globals={
            'AND_SEE_THE_GREAT_ACHILLES': AND_SEE_THE_GREAT_ACHILLES,
            'THO_MUCH_IS_TAKEN': THO_MUCH_IS_TAKEN,
            'we_are_not_now_that_strength_which_in_old_days': (
                we_are_not_now_that_strength_which_in_old_days),
        },
        func_locals={
            'Optional': Optional,
        },
        func_wrapped=we_are_not_now_that_strength_which_in_old_days,
    )

    # Assert this wrapper wrapped this wrappee.
    assert ulysses.__doc__ == (
        we_are_not_now_that_strength_which_in_old_days.__doc__)

    # Assert this wrapper returns an expected value.
    odyssey = ulysses('Made weak by time and fate, but strong in will')
    assert 'Made weak by time and fate, but strong in will' in odyssey

    # Arbitrary debuggable callable accessing no scoped attributes.
    to_strive_to_seek_to_find = make_func(
        func_name='to_strive_to_seek_to_find',
        func_code='''
def to_strive_to_seek_to_find(and_not_to_yield: str) -> str:
    return and_not_to_yield
''',
        # Print the definition of this callable to standard output, captured by
        # the "capsys" fixture passed above for testing against below.
        is_debug=True,
    )

    # Assert this callable returns an expected value.
    assert (
        to_strive_to_seek_to_find('Tis not too late to seek a newer world.') ==
        'Tis not too late to seek a newer world.'
    )

    # Pytest object freezing the current state of standard output and error as
    # uniquely written to by this unit test up to this statement.
    standard_captured = capsys.readouterr()

    # Assert the prior make_func() call printed the expected definition.
    assert standard_captured.out.count('\n') == 2
    assert 'line' in standard_captured.out
    assert 'def to_strive_to_seek_to_find(' in standard_captured.out
    assert 'return and_not_to_yield' in standard_captured.out

    # Assert the prior make_func() call cached the expected definition.
    func_filename = to_strive_to_seek_to_find.__code__.co_filename
    func_cache = linecache_cache.get(func_filename)
    assert isinstance(func_cache, tuple)
    assert len(func_cache) == 4
    assert isinstance(func_cache[0], int)
    assert func_cache[1] is None
    assert func_cache[3] == func_filename
    func_cache_code = ''.join(func_cache[2])
    assert 'def to_strive_to_seek_to_find(' in func_cache_code
    assert 'return and_not_to_yield' in func_cache_code


def test_make_func_fail() -> None:
    '''
    Test unsuccessful usage of the
    :func:`beartype._util.func.utilfuncmake.make_func` function.
    '''

    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorWrapperException
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype._util.func.utilfuncmake import make_func
    from pytest import raises

    # Assert that attempting to create a function whose name collides with that
    # of a caller-defined local variable raises the expected exception.
    with raises(_BeartypeUtilCallableException):
        make_func(
            func_name='come_my_friends',
            func_code='''
def come_my_friends(T: str) -> str:
    return T + 'is not too late to seek a newer world'
''',
            func_label='Magnanimous come_my_friends() function',
            func_locals={
                'come_my_friends': 'Push off, and sitting well in order smite',
            },
        )

    # Assert that attempting to execute a syntactically invalid snippet raises
    # the expected exception.
    with raises(BeartypeDecorWrapperException):
        make_func(
            func_name='to_sail_beyond_the_sunset',
            func_code='''
def to_sail_beyond_the_sunset(and_the_baths: str) -> str:
    Of all the western stars, until I die.
''',
            func_label='Heroic to_sail_beyond_the_sunset() function',
            exception_cls=BeartypeDecorWrapperException,
        )

    # Assert that attempting to execute a syntactically valid snippet failing
    # to declare this function raises the expected exception.
    with raises(BeartypeDecorWrapperException):
        make_func(
            func_name='you_and_i_are_old',
            func_code='''
def old_age_hath_yet_his_honour_and_his_toil() -> str:
    return 'Death closes all: but something ere the end'
''',
            func_label='Geriatric you_and_i_are_old() function',
            exception_cls=BeartypeDecorWrapperException,
        )
