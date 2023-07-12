#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Callable scope utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.utilfunc.utilfuncscope` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ CLASSES                            }....................
class WhenOwlsCallTheBreathlessMoon(object):
    '''
    Arbitrary class declaring an arbitrary method.
    '''

    def in_the_blue_veil_of_the_night(self) -> None:
        '''
        Arbitrary method.
        '''

        pass

# ....................{ DECORATORS                         }....................
def attach_func_locals(**kwargs) -> 'collections.abc.Callable':
    '''
    Decorator attaching the local scope of the parent callable declaring the
    passed callable to a new ``func_locals`` attribute of the passed callable.

    Parameters
    ----------
    This decorator forwards all passed keyword parameters as is to the
    :func:`beartype._util.func.utilfuncscope.get_func_locals` getter.
    '''

    # Defer scope-specific imports for sanity.
    from beartype._util.func.utilfuncscope import get_func_locals

    def _attach_func_locals(func) -> 'collections.abc.Callable':
        '''
        Inner decorator satisfying Python's abstruse decorator design pattern.
        '''

        # Attach the local scope of that parent callable to the passed callable.
        func.func_locals = get_func_locals(func=func, **kwargs)

        # Reduce to the identity decorator.
        return func

    # Return this inner decorator.
    return _attach_func_locals

# ....................{ CALLABLES                          }....................
def when_in_the_springtime_of_the_year():
    '''
    Arbitrary callable declaring an arbitrary nested callable.
    '''

    # Defer scope-specific imports for sanity.
    from beartype.typing import Union

    # Arbitrary PEP-compliant type hint localized to this parent callable.
    type_hint = Union[int, str]

    @attach_func_locals(func_stack_frames_ignore=1)
    def when_the_trees_are_crowned_with_leaves() -> type_hint:
        '''
        Arbitrary nested callable annotated by a PEP-compliant type hint
        localized to the parent callable and decorated by a decorator attaching
        the local scope of that parent callable to a new ``func_locals``
        attribute of this nested callable.
        '''

        return 'When the ash and oak, and the birch and yew'

    # Return this nested callable.
    return when_the_trees_are_crowned_with_leaves


def long_past_their_woodland_days():
    '''
    Arbitrary callable declaring an arbitrary deeply nested class hierarchy
    declaring an arbitrary deeply nested callable.
    '''

    # Defer scope-specific imports for sanity.
    from typing import Union

    # Arbitrary PEP-compliant type hint localized to this parent callable.
    type_hint = Union[bool, str]

    class TheShadowsOfTheTreesAppear(object):
        class AmidstTheLanternLight(object):
            @attach_func_locals(
                # Ignore both this nested "AmidstTheLanternLight" class and its
                # parent "TheShadowsOfTheTreesAppear" class when searching for
                # the closure lexical scope declaring the "type_hint" local.
                func_scope_names_ignore=2,
                func_stack_frames_ignore=1,
            )
            def weve_been_rambling_all_the_night(self) -> type_hint:
                '''
                Arbitrary nested callable annotated by a PEP-compliant type hint
                localized to the parent callable and decorated by a decorator
                attaching the local scope of that parent callable to a new
                ``func_locals`` attribute of this nested callable.
                '''

                return 'And some time of this day'

    # Return the root class of this class hierarchy.
    return TheShadowsOfTheTreesAppear

# ....................{ TESTS ~ tester                     }....................
def test_is_func_nested() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfuncscope.is_func_nested` tester.
    '''

    # Defer test-specific imports.
    from beartype._util.func.utilfunctest import is_func_nested

    # Nested callable returned by the above callable.
    when_the_ash_and_oak_and_the_birch_and_yew = (
        when_in_the_springtime_of_the_year())

    # Assert this tester accepts methods.
    assert is_func_nested(
        WhenOwlsCallTheBreathlessMoon.in_the_blue_veil_of_the_night) is True

    # Assert this tester accepts nested callables.
    # print(f'__nested__: {repr(when_the_ash_and_oak_and_the_birch_and_yew.__nested__)}')
    assert is_func_nested(when_the_ash_and_oak_and_the_birch_and_yew) is True

    # Assert this tester rejects non-nested parent callables declaring nested
    # callables.
    # print(f'__nested__: {repr(when_in_the_springtime_of_the_year.__nested__)}')
    assert is_func_nested(when_in_the_springtime_of_the_year) is False

    # Assert this tester rejects C-based builtins.
    assert is_func_nested(iter) is False


#FIXME: Unclear whether we'll ever require this, but preserved as is for now.
# def test_get_func_wrappee() -> None:
#     '''
#     Test the
#     :func:`beartype._util.func.utilfuncget.get_func_wrappee` function.
#     '''
#
#     # Defer test-specific imports.
#     from beartype.roar._roarexc import _BeartypeUtilCallableException
#     from beartype._util.func.utilfuncget import get_func_wrappee
#     from functools import wraps
#
#     # Arbitrary callable *NOT* decorated by @wraps.
#     def the_journey_begins_with_curiosity() -> str:
#         return 'And envolves into soul-felt questions'
#
#     # Arbitrary callable decorated by @wraps.
#     @wraps(the_journey_begins_with_curiosity)
#     def on_the_stones_that_we_walk() -> str:
#         return (
#             the_journey_begins_with_curiosity() +
#             'And choose to make our path'
#         )
#
#     # Assert this getter raises the expected exception when passed a callable
#     # *NOT* decorated by @wraps.
#     with raises(_BeartypeUtilCallableException):
#         get_func_wrappee(the_journey_begins_with_curiosity)
#
#     # Assert this getter returns the wrapped callable when passed a callable
#     # decorated by @wraps.
#     assert get_func_wrappee(on_the_stones_that_we_walk) is (
#         the_journey_begins_with_curiosity)

# ....................{ TESTS ~ getter                     }....................
def test_get_func_locals() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfuncscope.get_func_locals` getter.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilCallableException
    from beartype.typing import Union
    from beartype._util.func.utilfuncmake import make_func
    from beartype._util.func.utilfuncscope import get_func_locals
    from pytest import raises

    # ..................{ CALLABLES                          }..................
    def and_summon_the_shadows_there():
        '''
        Arbitrary nested callable.
        '''

        return 'And tie a ribbon on those sheltering arms'

    # Arbitrary nested callable dynamically declared in-memory.
    when_the_ash_and_oak_and_the_birch_and_yew = make_func(
        func_name='when_the_ash_and_oak_and_the_birch_and_yew',
        func_code='''def when_the_ash_and_oak_and_the_birch_and_yew(): pass''',
    )

    # Arbitrary nested callables whose unqualified and fully-qualified names
    # are maliciously desynchronized below, exercising edge cases.
    def are_dressed_in_ribbons_fair(): pass
    def who_will_go_down_to_the_shady_groves(): pass
    are_dressed_in_ribbons_fair.__qualname__ = (
        'when_owls_call.the_breathless_moon')
    who_will_go_down_to_the_shady_groves.__qualname__ = (
        '<locals>.who_will_go_down_to_the_shady_groves')

    # ..................{ PASS ~ noop                        }..................
    # Assert this getter returns the empty dictionary for callables dynamically
    # declared in-memory.
    assert get_func_locals(when_the_ash_and_oak_and_the_birch_and_yew) == {}

    # Assert this getter returns the empty dictionary for unnested callables.
    assert get_func_locals(when_in_the_springtime_of_the_year) == {}

    # Assert this getter returns the empty dictionary for nested callables
    # ignoring *ALL* of their parent lexical scopes.
    assert get_func_locals(
        func=and_summon_the_shadows_there, func_scope_names_ignore=1) == {}

    # ..................{ PASS ~ callable                    }..................
    # Arbitrary nested callable declared by a module-scoped callable.
    when_the_trees_are_crowned_with_leaves = (
        when_in_the_springtime_of_the_year())

    # Dictionary mapping from the name to value of all local attributes
    # accessible to that nested callable.
    func_locals = when_the_trees_are_crowned_with_leaves.func_locals

    # Assert this dictionary contains the name of the local attribute annotating
    # that nested callable's return.
    func_locals_return = func_locals.get('type_hint')
    assert func_locals_return == Union[int, str]

    # ..................{ PASS ~ class                       }..................
    # Arbitrary root nested class declared by a module-scoped callable.
    TheShadowsOfTheTreesAppear = long_past_their_woodland_days()

    # Method lexically nested inside that root nested class.
    weve_been_rambling_all_the_night = (
        TheShadowsOfTheTreesAppear.AmidstTheLanternLight.weve_been_rambling_all_the_night)

    # Dictionary mapping from the name to value of all local attributes
    # accessible to that method.
    func_locals = weve_been_rambling_all_the_night.func_locals

    # Assert this dictionary contains the name of the local attribute annotating
    # that nested callable's return.
    func_locals_return = func_locals.get('type_hint')
    assert func_locals_return == Union[bool, str]

    # ..................{ FAIL                               }..................
    # Assert this getter raises the expected exception for nested callables
    # whose unqualified and fully-qualified names are desynchronized.
    with raises(_BeartypeUtilCallableException):
        get_func_locals(are_dressed_in_ribbons_fair)

    # Assert this getter raises the expected exception for nested callables
    # whose fully-qualified name is prefixed by "<locals>".
    with raises(_BeartypeUtilCallableException):
        get_func_locals(who_will_go_down_to_the_shady_groves)

    # Assert this getter raises the expected exception for nested callables
    # erroneously ignoring more parent lexical scopes than actually exist.
    with raises(_BeartypeUtilCallableException):
        get_func_locals(
            func=and_summon_the_shadows_there,
            func_scope_names_ignore=2,
        )

# ....................{ TESTS ~ adder                      }....................
def test_add_func_scope_attr() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfuncscope.add_func_scope_attr` adder.
    '''

    # Defer test-specific imports.
    from beartype._util.func.utilfuncscope import add_func_scope_attr

    # Arbitrary scope to add attributes to.
    func_scope = {}

    # Arbitrary object to be added to this scope.
    attr = 'Pestilence-stricken multitudes: O thou,'

    # Named of this attribute in this scope.
    attr_name = add_func_scope_attr(attr=attr, func_scope=func_scope)

    # Assert the prior call added this attribute to this scope as expected.
    assert isinstance(attr_name, str)
    assert str(id(attr)) in attr_name
    assert func_scope[attr_name] is attr

    # Assert this getter returns the same name when repassed an attribute
    # previously added to this scope.
    assert add_func_scope_attr(attr=attr, func_scope=func_scope) == attr_name
    assert func_scope[attr_name] is attr

    # Note that testing this getter's error condition is effectively
    # infeasible, as doing so would require deterministically creating a
    # different object with the same object identifier. *sigh*
