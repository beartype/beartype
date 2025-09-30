#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide **beartype import hookable decorator-hostile decorator submodule**
(i.e., defining callables decorated by chains of one or more **decorator-hostile
decorators** (i.e., decorators hostile to other decorators by prohibiting other
decorators from being applied after they themselves are applied in such a chain)
into which the :mod:`beartype.beartype` decorator will be injected after the
last decorator-hostile decorator, mimicking real-world usage of the
:func:`beartype.claw.beartype_package` import hook from external callers).
'''

# ....................{ TODO                               }....................
#FIXME: Also test chains of two or more (ideally, three) decorators both
#containing and *NOT* containing the @typing.no_type_check decorator. Note that
#decorator, decorator_isomorphic, and decorator_nonisomorphic are also useful
#decorators here.

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeCallHintReturnViolation
from pytest import raises

# ....................{ IMPORTS                            }....................
# Exercise all possible kinds of imports of this decorator-hostile decorator.

# Import this decorator-hostile decorator directly as an attribute from the
# nested submodule defining this decorator with an absolute import-from
# statement.
from beartype_test.a00_unit.data.func.data_decor import (
    DecoratorHostileWrapper,
    decorator_hostile,

    # Import this same decorator-hostile decorator under an aliased name.
    decorator_hostile as decorator_hostile_alias,

    # Import additional decorator-friendly decorators as well.
    decorator,
    decorator_isomorphic,
    decorator_nonisomorphic,
)

# Import the root package transitively defining this decorator with an absolute
# import statement.
import beartype_test

# Import the nested submodule defining this decorator with an absolute
# import-from statement.
from beartype_test.a00_unit.data.func import data_decor

# Import a nested submodule transitively defining this decorator with a relative
# import-from statement.
from ..... import func

# ....................{ FUNCTIONS                          }....................
# Validate that the import hook presumably registered by the caller implicitly
# injects the @beartype decorator *AFTER* the last decorator-hostile decorator
# in all chains of callable decorations.

@decorator_hostile
def roused_from_icy_trance() -> int:
    '''
    Arbitrary function trivially violating its return type hint, decorated by a
    decorator-hostile decorator function directly imported as an attribute from
    the submodule defining that function.
    '''

    return "Even now, while Saturn, rous'd from icy trance,"


@decorator_hostile_alias
def his_palace_door_flew_ope() -> int:
    '''
    Arbitrary function trivially violating its return type hint, decorated by a
    decorator-hostile decorator function directly imported as an attribute from
    the submodule defining that function aliased to a different local name.
    '''

    return 'Then, as was wont, his palace-door flew ope'


@beartype_test.a00_unit.data.func.data_decor.decorator_hostile
def thea_through_the_woods() -> int:
    '''
    Arbitrary function trivially violating its return type hint, decorated by a
    decorator-hostile decorator function accessed via the root package
    transitively defining that function.
    '''

    return 'Went step for step with Thea through the woods,'


@data_decor.decorator_hostile
def twilight_in_the_rear() -> int:
    '''
    Arbitrary function trivially violating its return type hint, decorated by a
    decorator-hostile decorator function accessed via the nested submodule
    directly defining that function.
    '''

    return 'Hyperion, leaving twilight in the rear,'


#FIXME: Currently emits a warning. *sigh*
# @func.data_decor.decorator_hostile
# def threshold_of_the_west() -> int:
#     '''
#     Arbitrary function trivially violating its return type hint, decorated by a
#     decorator-hostile decorator function accessed via a nested submodule only
#     transitively defining that function.
#     '''
#
#     return 'Came slope upon the threshold of the west;'

# ....................{ LOCALS                             }....................
# Tuple of all decorator-hostile decorator-decorated callables defined above.
FUNCS_DECOR_HOSTILE = (
    roused_from_icy_trance,
    his_palace_door_flew_ope,
    thea_through_the_woods,
    twilight_in_the_rear,

    #FIXME: Currently raises an exception. *sigh*
    # threshold_of_the_west,
)

# ....................{ ASSERTS                            }....................
# For each decorator-hostile decorator-decorated callable defined above...
for func_decor_hostile in FUNCS_DECOR_HOSTILE:
    # ....................{ PASS                               }....................
    # Assert that the import hook registered by the caller preserved the
    # uncallable object created and returned by the decorator-hostile decorator
    # decorating the callables defined above.
    assert isinstance(func_decor_hostile, DecoratorHostileWrapper)

    # ....................{ FAIL                               }....................
    # Assert that the import hook registered by the caller injected the
    # @beartype decorator *AFTER* the last decorator-hostile decorator
    # decorating the callables defined above.
    with raises(BeartypeCallHintReturnViolation):
        func_decor_hostile.invoke()
