#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator non-class decoration** unit tests.

This submodule unit tests high-level functionality of the
:func:`beartype.beartype` decorator with respect to decorating **non-classes**
(e.g., unbound functions) irrespective of lower-level type hinting concerns
(e.g., PEP-compliance and -noncompliance).
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import (
    skip_if_python_version_greater_than_or_equal_to,
    skip_if_python_version_less_than,
)

# ....................{ TESTS ~ wrapper                    }....................
def test_decor_nontype_wrapper_isomorphic() -> None:
    '''
    Test the :func:`beartype.beartype` decorator on **isomorphic wrappers**
    (i.e., callables decorated by the standard :func:`functools.wraps` decorator
    for wrapping pure-Python callables with additional functionality defined by
    higher-level decorators such that those wrappers isomorphically preserve
    both the number and types of all passed parameters and returns by accepting
    only a variadic positional argument and a variadic keyword argument).
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from collections.abc import Callable
    from functools import wraps
    from pytest import raises

    # ....................{ WRAPPERS                       }....................
    def hang_their_mute_thoughts(on_the_mute_walls_around: str) -> int:
        '''
        Arbitrary **undecorated wrappee** (i.e., lower-level callable wrapped by
        the higher-level :func:`hang_their_mute_thoughts` wrapper intentionally
        *not* decorated by the :func:`.beartype` decorator).
        '''

        return len(on_the_mute_walls_around)


    @beartype
    @wraps(hang_their_mute_thoughts)
    def he_lingered(*args, **kwargs):
        '''
        Arbitrary **decorated isomorphic non-closure wrapper** (i.e., isomorphic
        wrapper defined as a function rather than closure, decorated by the
        :func:`.beartype` decorator).
        '''

        return hang_their_mute_thoughts(*args, **kwargs)


    @beartype
    def of_the_worlds_youth(func: Callable) -> Callable:
        '''
        Arbitrary **decorated isomorphic non-closure wrapper decorator** (i.e.,
        decorator function creating and returning an isomorphic wrapper defined
        as a closure, all decorated by the :func:`.beartype` decorator).
        '''

        @beartype
        @wraps(func)
        def through_the_long_burning_day(*args, **kwargs):
            '''
            Arbitrary **decorated isomorphic closure wrapper** (i.e., isomorphic
            wrapper defined as a closure, decorated by the :func:`.beartype`
            decorator).
            '''

            return func(*args, **kwargs)

        # Return this wrapper.
        return through_the_long_burning_day


    # Isomorphic closure wrapper created and returned by the above decorator.
    when_the_moon = of_the_worlds_youth(hang_their_mute_thoughts)

    # ....................{ PASS                           }....................
    # Assert that these wrappers passed valid parameters return the expected
    # values.
    assert he_lingered('He lingered, poring on memorials') == 32
    assert when_the_moon(
        'Gazed on those speechless shapes, nor, when the moon') == 52

    # ....................{ FAIL                           }....................
    # Assert that these wrappers passed invalid parameters raise the expected
    # exceptions.
    with raises(BeartypeCallHintParamViolation):
        he_lingered(b"Of the world's youth, through the long burning day")
    with raises(BeartypeCallHintParamViolation):
        when_the_moon(b"Filled the mysterious halls with floating shades")


def test_decor_nontype_wrapper_type() -> None:
    '''
    Test the :func:`beartype.beartype` decorator on **type wrappers**
    (i.e., types decorated by the standard :func:`functools.wraps` decorator
    for wrapping arbitrary types with additional functionality defined by
    higher-level decorators, despite the fact that wrapping types does *not*
    necessarily make as much coherent sense as one would think it does).
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.typing import Any
    from functools import wraps

    # ....................{ WRAPPERS                       }....................
    @beartype
    @wraps(list)
    def that_echoes_not_my_thoughts(*args: Any, **kwargs: Any):
        '''
        Arbitrary **decorated type non-closure wrapper** (i.e., wrapper defined
        as a function wrapped by an arbitrary type decorated by the
        :func:`.beartype` decorator).
        '''

        return list(*args, **kwargs)

    # ....................{ ASSERTS                        }....................
    # Assert that this wrapper passed valid parameters returns the expected
    # value.
    assert that_echoes_not_my_thoughts(('A', 'gloomy', 'smile',)) == [
        'A', 'gloomy', 'smile']

# ....................{ TESTS ~ fail : wrappee             }....................
def test_decor_nontype_type_fail() -> None:
    '''
    Test unsuccessful usage of the :func:`beartype.beartype` decorator for an
    **invalid wrappee** (i.e., object *not* decoratable by this decorator).
    '''

    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeDecorWrappeeException
    from pytest import raises

    # Assert that decorating an uncallable object raises the expected
    # exception.
    with raises(BeartypeDecorWrappeeException):
        beartype(('Book of the Astronomican', 'Slaves to Darkness',))
