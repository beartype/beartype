#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) stringified forward
reference type-checking** unit tests.

This submodule unit tests the subset of the public API of the public
:mod:`beartype.door` subpackage that pertains to type-checking
:pep:`484`-compliant stringified forward reference type hints.

This submodule intentionally resides in the
:mod:`beartype_test.a00_unit.a60_decor` rather than more superficially suitable
:mod:`beartype_test.a00_unit.a50_check.a90_door` subpackage. Why?
Maintainability. Aggregating all tests testing stringified forward references
into a common subpackage substantially reduces cognitive load while debugging.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_pep484_ref_door() -> None:
    '''
    Test the :mod:`beartype.door` API with respect to :pep:`484`-compliant
    stringified forward reference type hints.

    Resolving forward references in statement-time type-checkers published by
    the :mod:`beartype.door` subpackage fundamentally differs from
    decoration-time type-checking wrappers produced by the
    :func:`beartype.beartype` decorator. Specifically:

    * Statement-time type-checkers resolve forward references against the first
      third-party lexical scope on the current call stack and thus require call
      stack introspection.
    * Decoration-time type-checkers resolve forward references against the
      currently decorated callable (and possibly type) and thus require no call
      stack introspection.
    '''

    # ..................{ IMPORTS                            }..................
    from beartype.door import (
        TypeHint,
        die_if_unbearable,
        is_bearable,
    )
    from beartype.roar import BeartypeDoorHintViolation
    from pytest import raises
    from typing import Union

    # ..................{ HINTS                              }..................
    # PEP 484-compliant union of a trivial child hint with a PEP 484-compliant
    # stringified forward reference to the local type defined below (in the
    # opposite of the optimal order).
    #
    # Note that order of child hints is *EXTREMELY* significant. To replicate
    # worst-case end user behaviour, these child hints are intentionally ordered
    # in a erroneous manner. Doing so validates that our code generator
    # intentionally destroys (rather than preserves) this order when it
    # dynamically generates type-checking code. Our code generator reduces the
    # likelihood that union type-checks will raise unexpected exceptions by
    # "short-circuiting" those type-checks as follows:
    # * Prepending unions with child hints whose resolution is trivial (e.g.,
    #   the "None" singleton, which is *ALWAYS* guaranteed to exist).
    # * Appending unions with child hints whose resolution is non-trivial or
    #   possibly even infeasible at various type-checking times (e.g.,
    #   stringified forward references to undefined types).
    to_the_ocean_waves = Union['RollsItsLoudWaters', None]

    # Type hint wrapper encapsulating this union.
    a_mist_arose = TypeHint(to_the_ocean_waves)

    # ..................{ PASS                               }..................
    # Assert that statement-level type-checkers accept PEP-compliant union type
    # hints containing one or more unresolvable stringified forward references
    # (e.g., referring to types that have yet to be defined) *WITHOUT* raising
    # exceptions. See above for discussion.
    assert is_bearable(None, to_the_ocean_waves) is True
    assert a_mist_arose.is_bearable(None) is True
    die_if_unbearable(None, to_the_ocean_waves)
    a_mist_arose.die_if_unbearable(None)

    # ..................{ CLASSES                            }..................
    class RollsItsLoudWaters(object):
        '''
        Arbitrary class against which to test relative forward references below.

        This class is intentionally defined in a local rather than global scope,
        validating that statement-time type-checkers are able to resolve
        relative forward references to local attributes *only* accessible by
        introspecting the current call stack.
        '''

        pass

    # Arbitrary instance of this class.
    breathes_its_swift_vapours = RollsItsLoudWaters()

    # Arbitrary object violating the union type hint defined above.
    to_the_circling_air = 'Breathes its swift vapours to the circling air.'

    # ..................{ PASS                               }..................
    # Assert that statement-level type-checkers accept PEP-compliant union type
    # hints containing one or more resolvable stringified forward references
    # (e.g., referring to types that have now been defined) *WITHOUT* raising
    # exceptions.
    assert is_bearable(breathes_its_swift_vapours, to_the_ocean_waves) is True
    assert a_mist_arose.is_bearable(breathes_its_swift_vapours) is True
    die_if_unbearable(breathes_its_swift_vapours, to_the_ocean_waves)
    a_mist_arose.die_if_unbearable(breathes_its_swift_vapours)

    # ..................{ FAIL                               }..................
    # Assert that statement-level type-checkers reject objects violating
    # PEP-compliant union type hints containing one or more resolvable
    # stringified forward references (e.g., referring to types that have now
    # been defined) *WITHOUT* raising unexpected exceptions.
    assert is_bearable(to_the_circling_air, to_the_ocean_waves) is False
    assert a_mist_arose.is_bearable(to_the_circling_air) is False
    with raises(BeartypeDoorHintViolation):
        die_if_unbearable(to_the_circling_air, to_the_ocean_waves)
    with raises(BeartypeDoorHintViolation):
        a_mist_arose.die_if_unbearable(to_the_circling_air)
