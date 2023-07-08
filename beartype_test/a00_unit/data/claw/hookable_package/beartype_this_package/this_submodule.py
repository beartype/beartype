#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **current package beartype import hooked submodule** (i.e., data
module mimicking real-world usage of the
:func:`beartype.claw.beartype_this_package` import hook from an arbitrarily
deeply nested submodule ``{some_package}...{some_submodule}` of an arbitrary
third-party package ``{some_package}``).
'''

# ....................{ IMPORTS                            }....................
from beartype import beartype
from beartype.roar import (
    BeartypeCallHintParamViolation,
    BeartypeCallHintReturnViolation,
    BeartypeDoorHintViolation,
)
from beartype.typing import (
    # Iterable,
    List,
    Optional,
    Union,
)
from pytest import raises

#FIXME: Fascinatingly, this doesn't actually test anything. Why? We have *NO*
#idea whatsoever, but strongly suspect that pytest's own import hooks are
#silently conflicting with @beartype's in a manner preventing @beartype from
#guarding against regressions in this functionality. For now, the *ONLY* means
#of testing this is to do so manually in an external module subject to a
#beartype import hook that performs this import. Gag me with a spork.

# Intentionally import a pure-Python module from the standard library that
# internally imports a C extension -- in this case, "_struct". Doing so ensures
# that beartype import hooks properly support loading of C extensions, which our
# initial implementation did *NOT*. Avoid regressions by testing this, please.
import struct

# from beartype.claw._importlib.clawimpcache import module_name_to_beartype_conf
# print(f'this_submodule conf: {repr(module_name_to_beartype_conf)}')

# ....................{ PEP 526                            }....................
# Validate that the beartype_this_package() import hook installed by the parent
# "beartype_this_package.__init__" submodule implicitly appends all PEP
# 562-compliant annotated assignment statements in other submodules of this
# "beartype_this_package" subpackage with calls to beartype's statement-level
# beartype.door.die_if_unbearable() exception-raiser.

# Assert that a PEP 562-compliant assignment statement assigning an object
# satisfying the type hint annotating that statement raises *NO* exception.
#
# Note that this type hint is intentionally annotated as "float" rather than
# either "int" *OR* "Union[int, float]", exercising that that import hook
# successfully associated this and *ALL* other submodules of the
# "beartype_this_package" subpackage with a non-default beartype configuration
# enabling the PEP 484-compliant implicit numeric tower (i.e.,
# "is_pep484_tower=True").
loves_philosophy: float = len('The fountains mingle with the river')

# Assert that a PEP 562-compliant assignment statement assigning an object
# violating the type hint annotating that statement raises the expected
# exception.
with raises(BeartypeDoorHintViolation):
    and_the_rivers_with_the_ocean: List[str] = (
        'The winds of heaven mix for ever')

# ....................{ FUNCTIONS ~ accept                 }....................
# Functions whose type-checking implicitly accepts the non-default beartype
# configuration established by the sibling "__init__" submodule in this
# subpackage.

def nothing_in_the_world(is_single: Union[float, bytes]) -> Optional[complex]:
    '''
    Arbitrary method either returning the passed integer first doubled and then
    coerced into a complex number with imaginary component ``1`` if this integer
    is non-zero *or* raising a :exc:`.BeartypeCallHintParamViolation` exception
    otherwise (i.e., if this integer is zero), exercising that beartype import
    hooks decorate global functions as expected.
    '''

    def in_one_spirit(meet_and_mingle: Optional[float]) -> Union[complex, str]:
        '''
        Arbitrary closure either returning the passed integer first doubled and
        then coerced into a complex number with imaginary component ``1`` if
        this integer is non-:data:`None` *or* raising a
        :exc:`.BeartypeCallHintReturnViolation` exception otherwise (i.e., if
        this integer is :data:`None`), exercising that beartype import hooks
        decorate closures as expected.
        '''

        # Return either...
        return (
            # If this integer is "None", explicitly force this
            # @beartype-decorated closure to raise a
            # "BeartypeCallHintReturnViolation" exception;
            None
            if meet_and_mingle is None else
            # Else, this integer is non-"None". In this case, return this
            # integer doubled and then coerced into a complex number with
            # imaginary component "1". Why? Just because. *THIS IS BEARTYPE.*
            is_single + meet_and_mingle + 1j
        )

    # Return either...
    return (
        # If this integer is zero, explicitly force this @beartype-decorated
        # closure to raise a "BeartypeCallHintReturnViolation" exception.
        in_one_spirit(None)
        if is_single == 0 else
        # Else, this integer is non-zero. In this case, return this integer
        # doubled and then coerced into a complex number with imaginary
        # component "1". Why? Just because. *THIS IS BEARTYPE.* Graaaah!
        in_one_spirit(is_single)
    )

# Assert that calling this function passed an arbitrary integer returns the
# expected complex number *WITHOUT* raising an exception.
assert nothing_in_the_world(len('Why not I with thine?')) == 42 + 1j

# Assert that calling this function passed an invalid parameter raises the
# expected exception.
with raises(BeartypeCallHintParamViolation):
    nothing_in_the_world('See the mountains kiss high heaven')

# Assert that calling this function passed zero raises the expected exception
# from the closure defined and called by this function.
with raises(BeartypeCallHintReturnViolation):
    nothing_in_the_world(len('And the waves') - len('clasp another'))

# ....................{ FUNCTIONS ~ reject                 }....................
# Functions whose type-checking explicitly rejects the non-default beartype
# configuration established by the sibling "__init__" submodule in this
# subpackage (i.e., due to being decorated by the @beartype decorator implicitly
# configured by the default beartype configuration). In particular, these
# functions disable the PEP 484-compliant implicit numeric tower such that:
# * "float" just means "float" *WITHOUT* being expanded to "float | int".
# * "complex" just means "complex" *WITHOUT* being expanded to "complex | float
#   | int".

@beartype  # <-- prefer the default beartype configuration
def alastor_or(the_spirit_of_solitude: Union[float, bytes]) -> (
    Optional[complex]):
    '''
    Arbitrary method either returning the passed float first doubled and then
    coerced into a complex number with imaginary component ``1`` if this float
    is non-zero *or* raising a :exc:`.BeartypeCallHintParamViolation` exception
    otherwise (i.e., if this float is zero), exercising that beartype import
    hooks decorate global functions as expected.
    '''

    @beartype  # <-- prefer the default beartype configuration
    def nondum_amabam(et_amare_amabam: Optional[float]) -> Union[complex, str]:
        '''
        Arbitrary closure either returning the passed float first doubled and
        then coerced into a complex number with imaginary component ``1`` if
        this float is non-:data:`None` *or* raising a
        :exc:`.BeartypeCallHintReturnViolation` exception otherwise (i.e., if
        this float is :data:`None`), exercising that beartype import hooks
        decorate closures as expected.
        '''

        # Return either...
        return (
            # If this float is "None", explicitly force this
            # @beartype-decorated closure to raise a
            # "BeartypeCallHintReturnViolation" exception;
            None
            if et_amare_amabam is None else
            # Else, this float is non-"None". In this case, return this float
            # doubled and then coerced into a complex number with imaginary
            # component "1". Why? Just because. *THIS IS BEARTYPE.* Graaaah!
            the_spirit_of_solitude + et_amare_amabam + 1j
        )

    # Return either...
    return (
        # If this float is zero, explicitly force this @beartype-decorated
        # closure to raise a "BeartypeCallHintReturnViolation" exception.
        nondum_amabam(None)
        if the_spirit_of_solitude == 0.0 else
        # Else, this integer is non-zero. In this case, return this integer
        # doubled and then coerced into a complex number with imaginary
        # component "1". Why? Just because. *THIS IS BEARTYPE.* Graaaah!
        nondum_amabam(the_spirit_of_solitude)
    )


# Assert that calling this function passed an arbitrary float returns the
# expected complex number *WITHOUT* raising an exception.
assert alastor_or(len('Earth, ocean, air, beloved brotherhood!') + 0.0) == (
    78 + 1j)

# Assert that calling this function passed an invalid parameter raises the
# expected exception.
with raises(BeartypeCallHintParamViolation):
    alastor_or(len('If our great Mother has imbued my soul'))

# Assert that calling this function passed zero raises the expected exception
# from the closure defined and called by this function.
with raises(BeartypeCallHintReturnViolation):
    alastor_or(len('quid amarem') - len('amans amare') + 0.0)

# ....................{ CLASSES                            }....................
class ConfessStAugust(object):
    '''
    Arbitrary class to be implicitly decorated by the :func:`beartype.beartype`
    decorator by the :func:`beartype.claw.beartype_this_package` import hook
    installed by the parent ``beartype_this_package.__init__`` submodule.
    '''

    def with_aught_of_natural_piety(self, to_feel: Union[complex, str]) -> (
        Union[List[bytes], complex]):
        '''
        Arbitrary method accepting the passed object under the non-default
        beartype configuration established by the sibling ``__init__`` submodule
        in this subpackage and returning that object as is, enabling callers to
        trivially test whether any call to this method violates the type hints
        annotating this method.
        '''

        # Look, @beartype. Just do it!
        return to_feel


    @beartype  # <-- prefer the default beartype configuration
    def your_love(
        self, and_recompense_the_boon_with_mine: Union[complex, bool]) -> (
        Union[complex, List[bytes]]):
        '''
        Arbitrary method accepting the passed object under the default beartype
        configuration and returning that object as is, enabling callers to
        trivially test whether any call to this method violates the type hints
        annotating this method.
        '''

        # Look here, you. Just do it yet again!
        return and_recompense_the_boon_with_mine


# Arbitrary instance of this class.
if_dewy_morn = ConfessStAugust()

# Assert that calling the first method passed an arbitrary integer returns that
# integer as is *WITHOUT* raising an exception.
assert if_dewy_morn.with_aught_of_natural_piety(len(
    'If dewy morn, and odorous noon, and even')) == 40

# Assert that calling the first method passed an invalid parameter raises the
# expected exception.
with raises(BeartypeCallHintParamViolation):
    if_dewy_morn.with_aught_of_natural_piety(
        b'With sunset and its gorgeous ministers,')

# Assert that calling the second method passed an arbitrary complex number
# returns that complex number as is *WITHOUT* raising an exception.
assert if_dewy_morn.your_love(len(
    "And solemn midnight's tingling silentness;") + 1j) == 42 + 1j

# Assert that calling the second method passed an invalid parameter raises the
# expected exception.
with raises(BeartypeCallHintParamViolation):
    if_dewy_morn.your_love(len("If autumn's hollow sighs in the sere wood,"))
