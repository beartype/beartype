#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype callable source code file utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.func.utilfuncfile` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ tester                     }....................
def test_is_func_file() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfuncfile.is_func_file` tester.
    '''

    # Defer test-specific imports.
    from beartype._util.func.utilfuncfile import is_func_file

    # Arbitrary pure-Python callable declared on-disk.
    def but_now_thy_youngest_dearest_one_has_perished():
        return 'The nursling of thy widowhood, who grew,'

    # Arbitrary pure-Python callable declared in-memory *WITHOUT* being cached
    # by the standard "linecache" module.
    like_a_pale_flower = eval('lambda: "by some sad maiden cherished,"')

    # Assert this tester accepts pure-Python callables declared on-disk.
    assert is_func_file(but_now_thy_youngest_dearest_one_has_perished) is True

    # Assert this tester rejects pure-Python callables declared in-memory.
    assert is_func_file(like_a_pale_flower) is False

    # Assert this tester rejects C-based callables.
    assert is_func_file(iter) is False

# ....................{ TESTS ~ getter                     }....................
def test_get_func_filename_or_none() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfuncfile.get_func_filename_or_none` getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.func.utilfuncfile import get_func_filename_or_none
    from beartype._util.func.utilfuncmake import make_func

    # ....................{ CALLABLES                      }....................
    # Arbitrary pure-Python callable declared on-disk.
    def and_this_the_naked_countenance_of_earth():
        return 'On which I gaze, even these primeval mountains'

    # Arbitrary pure-Python callable declared in-memory cached by the standard
    # "linecache" module.
    like_snakes_that_watch_their_prey = make_func(
        func_name='like_snakes_that_watch_their_prey',
        func_code=(
            """
            like_snakes_that_watch_their_prey = lambda: (
                'from their far fountains,')
            """),
        is_debug=True,
    )

    # Arbitrary pure-Python callable declared in-memory *WITHOUT* being cached
    # by the standard "linecache" module.
    teach_the_adverting_mind = eval('lambda: "The glaciers creep"')

    # ....................{ ASSERTS                        }....................
    # Assert this getter returns "None" when passed a C-based callable.
    assert get_func_filename_or_none(iter) is None

    # Assert this getter returns the absolute filename of this submodule when
    # passed an on-disk pure-Python callable defined by this submodule.
    assert get_func_filename_or_none(
        and_this_the_naked_countenance_of_earth) == __file__

    # Assert this getter returns the placeholder filename associated with the
    # code object of a pure-Python callable defined in-memory cached by the
    # standard "linecache" module.
    assert get_func_filename_or_none(
        like_snakes_that_watch_their_prey) == (
        like_snakes_that_watch_their_prey.__code__.co_filename)

    # Assert this getter returns "None" when passed a pure-Python callable
    # defined in-memory *NOT* cached by the standard "linecache" module.
    assert get_func_filename_or_none(teach_the_adverting_mind) is None
