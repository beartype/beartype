#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Test-wide :pep:`484`-compliant **relative forward reference type hint utility**
unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.pep484.forward.pep484refrelative` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ getter                     }....................
def test_get_hint_pep484_ref_names_relative() -> None:
    '''
    Test the
    :func:`beartype._util.hint.pep.proposal.pep484.forward.pep484refrelative.get_hint_pep484_ref_names_relative`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintForwardRefException
    from beartype.typing import ForwardRef
    from beartype._util.hint.pep.proposal.pep484.forward.pep484refrelative import (
        get_hint_pep484_ref_names_relative)
    from pytest import raises

    # ....................{ LOCALS                         }....................
    # Arbitrary absolute forward references defined as strings.
    ALAS_ALAS = 'He_overleaps.the.bounds'
    BREATH_AND = 'Were.limbs_and.breath_and'

    # Arbitrary absolute forward reference defined as a non-string.
    BEING_INTERTWINED = ForwardRef(BREATH_AND)

    # Arbitrary fully-qualified names of a hypothetical module.
    OF_DIM_SLEEP = 'In_the.wide.pathless_desert'

    # Arbitrary relative forward reference defined as a string.
    THUS_TREACHEROUSLY = 'Lost_lost_for_ever_lost'

    # ....................{ PASS                           }....................
    # Assert this getter preserves the passed absolute forward reference as is
    # when defined as a string, regardless of whether the second passed object
    # defines the "__module__" dunder attribute.
    assert get_hint_pep484_ref_names_relative(ALAS_ALAS) == (None, ALAS_ALAS)

    # Assert this getter preserves the passed absolute forward reference as is
    # when defined as a non-string, regardless of whether the second passed
    # object defines the "__module__" dunder attribute.
    assert get_hint_pep484_ref_names_relative(BEING_INTERTWINED) == (None, BREATH_AND)

    # ....................{ PASS ~ module name             }....................
    # Since the active Python interpreter targets >= Python 3.10, then this
    # typing.ForwardRef.__init__() method accepts an additional optional
    # "module: Optional[str] = None" parameter preserving the fully-qualified
    # name of the module to which the passed unqualified basename is relative.
    # Assert that this getter successfully introspects that module name.

    # Arbitrary relative forward reference defined as a non-string relative to
    # the fully-qualified names of a hypothetical module.
    BEAUTIFUL_SHAPE = ForwardRef(THUS_TREACHEROUSLY, module=OF_DIM_SLEEP)

    # Arbitrary absolute forward reference defined as a non-string relative to
    # the fully-qualified names of a hypothetical module.
    #
    # Note that this exercises an edge case. Technically, passing both an
    # absolute forward reference *AND* a module names is a non-sequitur.
    # Pragmatically, the ForwardRef.__init__() method blindly permits callers to
    # do just that. Ergo, @beartype *MUST* guard against this.
    DARK_GATE_OF_DEATH = ForwardRef(ALAS_ALAS, module=OF_DIM_SLEEP)

    # Assert this getter canonicalizes the passed relative forward reference
    # against the fully-qualified names of the module with which this reference
    # was instantiated when defined as a non-string.
    assert get_hint_pep484_ref_names_relative(BEAUTIFUL_SHAPE) == (
        OF_DIM_SLEEP, THUS_TREACHEROUSLY)

    # Assert this getter preserves the passed absolute forward reference as is
    # *WITHOUT* canonicalizing this reference against the fully-qualified names
    # of the module with which this reference was instantiated when defined as a
    # non-string.
    assert get_hint_pep484_ref_names_relative(DARK_GATE_OF_DEATH) == (
        OF_DIM_SLEEP, ALAS_ALAS)

    # ....................{ FAIL                           }....................
    # Assert this getter raises the expected exception when passed a type hint
    # that is *NOT* a valid forward reference.
    with raises(BeartypeDecorHintForwardRefException):
        get_hint_pep484_ref_names_relative(
            b'Beyond the realms of dream that fleeting shade;')
