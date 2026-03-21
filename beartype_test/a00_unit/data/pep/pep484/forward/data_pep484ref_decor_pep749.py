#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide :pep:`484`-compliant **stringified forward reference type hint**
(i.e., strings whose values are the names of classes and tuples of classes, one
or more of which typically have yet to be defined) and :pep:`749`-compliant
**object-oriented forward reference type hint** (e.g.,
:class:`annotationlib.ForwardRef` objects serving a similar purpose) integration
data submodule.

This submodule exercises forward reference support implemented in the
:func:`beartype.beartype` decorator when specifically decorating callables
annotated by invalid forward references, regardless of whether those references
are :pep:`484`- or :pep:`749`-compliant. This submodule unifies common logic
broadly applicable to validating handling of both types of references.

Caveats
-------
**This submodule requires the active Python interpreter to target at least
Python 3.14.0.** If this is *not* the case, importing this submodule raises an
:exc:`SyntaxError` exception.
'''

# ....................{ IMPORTS                            }....................
from beartype import beartype
from beartype.roar import (
    BeartypeDecorHintPep484ForwardRefStrException,
    BeartypeDecorHintPep749ForwardRefObjectException,
)
from beartype_test.a00_unit.data import data_type
from beartype_test._util.pytroar import raises_uncached

# ....................{ GLOBALS                            }....................
data_type = data_type.Class()
'''
Arbitrary instance of an arbitrary type whose basename intentionally shadows
that of the submodule defining that type imported into this same global scope.
'''

# ....................{ FAIL ~ pep : 484                   }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: Synchronize with PEP 749-specific validation below.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Assert that the @beartype decorator raises the expected decoration-time
# exception when decorating problematic callables annotated by a stringified
# forward reference erroneously referring to non-existent attribute of the
# instance defined above.
with raises_uncached(BeartypeDecorHintPep484ForwardRefStrException) as (
    exception_info):
    @beartype
    def which_sages(and_keen_eyed_astrologers: 'data_type.Class') -> str:
        '''
        Arbitrary callable decorated by :func:`beartype.beartype`, annotated by
        a :pep:`484`-compliant stringified forward reference type hint referring
        to an undefined attribute of an arbitrary instance of an arbitrary type
        whose basename intentionally shadows that of the submodule defining that
        type imported into this same global scope, justifiably inducing a
        decoration-time exception from this decorator.

        Yes, this edge case actually happened. You can't make bugs like this up.

        See Also
        --------
        https://github.com/beartype/beartype/issues/527#issuecomment-4001362638
            Resolved issue validated by this callable.
        '''

        return "Which sages and keen-ey'd astrologers"

# Exception message raised by that decoration.
exception_message = str(exception_info.value)

# Assert that exception message contains a PEP-specific substring, indicating
# that the @beartype decorator correctly raised a human-readable exception.
assert ' PEP 484 ' in exception_message

# ....................{ FAIL ~ pep : 749                   }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# CAUTION: Synchronize with PEP 484-specific validation above.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Assert that the @beartype decorator raises the expected decoration-time
# exception when decorating problematic callables annotated by an unquoted
# forward reference erroneously referring to non-existent attribute of the
# instance defined above.
with raises_uncached(BeartypeDecorHintPep749ForwardRefObjectException) as (
    exception_info):
    @beartype
    def then_living(on_the_earth: data_type.Class) -> str:
        '''
        Arbitrary callable decorated by :func:`beartype.beartype`, annotated by
        a :pep:`749`-compliant object-oriented forward reference type hint
        referring to an undefined attribute of an arbitrary instance of an
        arbitrary type whose basename intentionally shadows that of the
        submodule defining that type imported into this same global scope,
        justifiably inducing a decoration-time exception from this decorator.

        Yes, this edge case actually happened. You can't make bugs like this up.

        See Also
        --------
        https://github.com/beartype/beartype/issues/527#issuecomment-4001362638
            Resolved issue validated by this callable.
        '''

        return "Then living on the earth, with labouring thought"

# Exception message raised by that decoration.
exception_message = str(exception_info.value)

# Assert that exception message contains a PEP-specific substring, indicating
# that the @beartype decorator correctly raised a human-readable exception.
assert ' PEP 749 ' in exception_message
