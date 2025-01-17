#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype decorator** :pep:`692`-compliant :obj:`typing.Self` **unit tests**.

This submodule unit tests :pep:`692` support implemented in the
:func:`beartype.beartype` decorator.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_if_python_version_less_than

# ....................{ TESTS                              }....................
@skip_if_python_version_less_than('3.12.0')
def test_decor_pep692() -> None:
    '''
    Test :pep:`692` support implemented in the :func:`beartype.beartype`
    decorator if the active Python interpreter targets Python >= 3.12 *or* skip
    otherwise.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeDecorHintPep692Exception
    from beartype.typing import (
        Tuple,
        TypedDict,
        Unpack,
    )
    from pytest import raises

    # ....................{ CLASSES                        }....................
    @beartype
    class BlueCavernMould(TypedDict):
        '''
        Typed dictionary annotating one or more arbitrary key-value pairs.
        '''

        nurses_of_rainbow_flowers: str
        and_branching_moss: bytes

    # ....................{ CALLABLES                      }....................
    @beartype
    def commit_the_colours(
        **kwargs: Unpack[BlueCavernMould]) -> str:
        '''
        Arbitrary callable decorated by :func:`beartype.beartype` accepting a
        variadic keyword parameter annotated by as a :pep:`692`-compliant
        unpacked typed dictionary subclass.
        '''

        # Return the string concatenation of these keyword arguments.
        return (
            kwargs['nurses_of_rainbow_flowers'] +
            kwargs['and_branching_moss'].decode('utf-8')
        )

    # ....................{ PASS                           }....................
    # Assert that this callable returns a tuple of all passed positional
    # parameters.
    assert commit_the_colours(
        nurses_of_rainbow_flowers='Commit the colours of ',
        and_branching_moss=b'that varying cheek,',
    ) == 'Commit the colours of that varying cheek,'

    # ....................{ FAIL                           }....................
    #FIXME: Additionally assert that calling the above commit_the_colours()
    #function with unrecognized or invalid keyword arguments raises the expected
    #type-checking violation *AFTER* we actually deeply support PEP 692.

    # Assert that @beartype raises the expected exception when decorating a
    # callable accepting a variadic keyword parameter annotated by a hint
    # unpacking a PEP 692-noncompliant object (i.e., *ANY* object other than a
    # PEP 692-compliant typed dictionary subclass).
    with raises(BeartypeDecorHintPep692Exception):
        @beartype
        def that_snowy_breast(
            **those_dark_and_drooping_eyes: Unpack[Tuple[str]]) -> str:
            return next(iter(those_dark_and_drooping_eyes.keys()))
