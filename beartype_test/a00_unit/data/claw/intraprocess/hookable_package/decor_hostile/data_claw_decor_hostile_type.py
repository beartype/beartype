#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide **beartype import hookable decorator-hostile decorator method
submodule** (i.e., defining callables decorated by chains of one or more
**decorator-hostile decorator method** (i.e., decorators implemented as methods
but hostile to other decorators by prohibiting other decorators from being
applied after they themselves are applied in such a chain) into which the
:mod:`beartype.beartype` decorator will be injected after the last
decorator-hostile decorator, mimicking real-world usage of the
:func:`beartype.claw.beartype_package` import hook from external callers).
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeCallHintReturnViolation
from pytest import raises

# ....................{ IMPORTS                            }....................
# Exercise all possible kinds of imports of this decorator-hostile decorator
# type.

# Import this decorator-hostile decorator type directly as an attribute from
# the nested submodule defining this type decorator via an absolute
# import-from statement.
from beartype_test.a00_unit.data.func.data_decor import (
    DecoratorHostileWrapper,
    DecoratorHostileType,

    # Import this same type under an aliased name.
    DecoratorHostileType as DecoratorHostileTypeAlias,
)

# Import the root package transitively defining this type with an absolute
# import statement.
import beartype_test

# Import the nested submodule defining this decorator with an absolute
# import-from statement.
from beartype_test.a00_unit.data.func import data_decor

# Import a nested submodule transitively defining this type with a relative
# import-from statement.
from ..... import func

# ....................{ FACTORIES                          }....................
def make_decorator_hostile_instance() -> DecoratorHostileType:
    '''
    Factory function creating and returning a new instance of the
    decorator-hostile decorator type imported above, intentionally obfuscating
    the instantiation of this type behind a function call.
    '''

    # Truly, one-liners win all lines.
    return DecoratorHostileType()

# ....................{ LOCALS                             }....................
# Validate that the import hook presumably registered by the caller implicitly
# detects instantiations of the decorator-hostile decorator type imported above,
# regardless of exactly how that type was imported.

and_like_a_rose: DecoratorHostileType = make_decorator_hostile_instance()
'''
Arbitrary instance of a decorator-hostile decorator type instantiated via an
intentionally obfuscatory factory function and thus explicitly annotated as
being an instance of that type by a :pep:`526`-compliant annotated variable
assignment.
'''


slow_breathed_melodies = DecoratorHostileType()
'''
Arbitrary instance of a decorator-hostile decorator type, directly imported as
an attribute from the submodule defining that type.
'''


in_vermeil = DecoratorHostileTypeAlias()
'''
Arbitrary instance of a decorator-hostile decorator type, directly imported as
an attribute from the submodule defining that type aliased to a different local
name.
'''


tint_and_shape = (
    beartype_test.a00_unit.data.func.data_decor.DecoratorHostileType())
'''
Arbitrary instance of a decorator-hostile decorator type, accessed via the root
package transitively defining that type.
'''


in_fragrance_soft = data_decor.DecoratorHostileType()
'''
Arbitrary instance of a decorator-hostile decorator type, accessed via the
nested submodule directly defining that type.
'''


and_coolness_to_the_eye = func.data_decor.DecoratorHostileType()
'''
Arbitrary instance of a decorator-hostile decorator type, accessed via a
nested submodule only transitively defining that type.
'''

# ....................{ CALLABLES                          }....................
# Validate that the import hook presumably registered by the caller implicitly
# injects the @beartype decorator *AFTER* the first decorator-hostile decorator
# method in all chains of callable decorations.
#
# Note that the abstract syntax tree (AST) transform performing this injection
# is rather crudely implemented and thus detects only trivial global and local
# attribute names. Since "for" loop variables are *NOT* detected, we manually
# define one callable decorated by each such instance (rather than automating
# these callable definitions in a "for" loop).

@and_like_a_rose.decorator_hostile_method
def that_inlet() -> int:
    '''
    Arbitrary function trivially violating its return type hint, decorated by a
    decorator-hostile decorator method bound to a type instantiated via an
    intentionally obfuscatory factory function and thus explicitly annotated as
    being an instance of that type by a :pep:`526`-compliant annotated variable
    assignment.
    '''

    return 'That inlet to severe magnificence'


@slow_breathed_melodies.decorator_hostile_method
def to_severe_magnificence() -> int:
    '''
    Arbitrary function trivially violating its return type hint, decorated by a
    decorator-hostile decorator method bound to a type directly imported as an
    attribute from the submodule defining that type.
    '''

    return 'And gave a roar, as if of earthly fire,'


@in_vermeil.decorator_hostile_method
def stood_full_blown() -> int:
    '''
    Arbitrary function trivially violating its return type hint, decorated by a
    decorator-hostile decorator method bound to a type directly imported as an
    attribute from the submodule defining that type aliased to a different local
    name.
    '''

    return "That scar'd away the meek ethereal Hours"


@tint_and_shape.decorator_hostile_method
def to_enter_in() -> int:
    '''
    Arbitrary function trivially violating its return type hint, decorated by a
    decorator-hostile decorator method bound to a type accessed via the root
    package transitively defining that type.
    '''

    return 'Stood full blown, for the God to enter in.'


@in_fragrance_soft.decorator_hostile_method
def he_entered() -> int:
    '''
    Arbitrary function trivially violating its return type hint, decorated by a
    decorator-hostile decorator method bound to a type accessed via the nested
    submodule directly defining that type.
    '''

    return "He enter'd, but he enter'd full of wrath;"


@and_coolness_to_the_eye.decorator_hostile_method
def full_of_wrath() -> int:
    '''
    Arbitrary function trivially violating its return type hint, decorated by a
    decorator-hostile decorator method bound to a type accessed via a nested
    submodule only transitively defining that type.
    '''

    return "His flaming robes stream'd out beyond his heels,"

# ....................{ LOCALS                             }....................
# Tuple of all decorator-hostile decorator-decorated callables defined above.
FUNCS_DECOR_HOSTILE_CHECKED = (
    that_inlet,
    to_severe_magnificence,
    stood_full_blown,
    to_enter_in,
    he_entered,
    full_of_wrath,
)

# ....................{ ASSERTS                            }....................
# For each decorator-hostile decorator-decorated callable defined above...
for func_decor_hostile_checked in FUNCS_DECOR_HOSTILE_CHECKED:
    # ....................{ PASS                           }....................
    # Assert that the import hook registered by the caller preserved the
    # uncallable object created and returned by the decorator-hostile decorator
    # decorating the callables defined above.
    assert isinstance(func_decor_hostile_checked, DecoratorHostileWrapper)

    # ....................{ FAIL                           }....................
    # Assert that the import hook registered by the caller injected the
    # @beartype decorator *AFTER* the last decorator-hostile decorator
    # decorating the callables defined above.
    with raises(BeartypeCallHintReturnViolation):
        func_decor_hostile_checked.invoke()
