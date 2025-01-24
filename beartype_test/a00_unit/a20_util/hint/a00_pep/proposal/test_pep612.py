#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide :pep:`612` **type hint utility** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.pep612` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ getter                     }....................
def test_get_hint_pep612_paramspec() -> None:
    '''
    Test the private
    :mod:`beartype._util.hint.pep.proposal.pep612.get_hint_pep612_paramspec`
    getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.api.standard.utiltyping import import_typing_attr_or_none
    from beartype._util.hint.pep.proposal.pep612 import (
        get_hint_pep612_paramspec)

    # ....................{ LOCALS                         }....................
    # PEP 612-compliant "typing(|_extensions).ParamSpec" class if importable
    # *OR* "None" otherwise.
    ParamSpec = import_typing_attr_or_none('ParamSpec')

    # If this class is unimportable, silently reduce to a noop.
    if ParamSpec is None:
        return
    # Else, this class is importable.

    # Arbitrary parameter specification.
    P = ParamSpec('P')

    # ....................{ ASSERTS                        }....................
    # Assert that this getter when passed an instance variable of this parameter
    # specification returns this same parameter specification.
    assert get_hint_pep612_paramspec(P.args) is P
    assert get_hint_pep612_paramspec(P.kwargs) is P

# ....................{ TESTS ~ maker                      }....................
def test_make_hint_pep612_concatenate_list_or_none() -> None:
    '''
    Test the private
    :mod:`beartype._util.hint.pep.proposal.pep612.make_hint_pep612_concatenate_list_or_none`
    factory.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.api.standard.utiltyping import (
        import_typing_attr,
        import_typing_attr_or_none,
    )
    from beartype._util.hint.pep.proposal.pep612 import (
        make_hint_pep612_concatenate_list_or_none)

    # ....................{ LOCALS                         }....................
    # PEP 612-compliant "typing(|_extensions).ParamSpec" class if importable
    # *OR* "None" otherwise.
    ParamSpec = import_typing_attr_or_none('ParamSpec')

    # If this class is unimportable...
    if ParamSpec is None:
        # Assert that this maker when passed an arbitrary list and an arbitrary
        # child type hint returns "None"
        assert make_hint_pep612_concatenate_list_or_none([], ...) is None
    # Else, this class is importable.

    # PEP 612-compliant "typing(|_extensions).Concatenate" type hint factory if
    # importable *OR* raise an exception otherwise. Since "ParamSpec" is
    # importable, "Concatenate" should be as well. *SHOULD* be...
    Concatenate = import_typing_attr('Concatenate')

    # Arbitrary parameter specification.
    P = ParamSpec('P')

    # ....................{ ASSERTS                        }....................
    # Assert that this maker when passed an empty list and this parameter
    # specification returns a "Concatenate[...]" type hint subscripted only by
    # this parameter specification.
    assert make_hint_pep612_concatenate_list_or_none([], P) == (
        Concatenate[P])

    # Assert that this maker when passed a non-empty list containing one or more
    # child type hints and a parameter specification returns a
    # "Concatenate[...]" type hint subscripted by all child type hints in this
    # list followed by this parameter specification.
    assert make_hint_pep612_concatenate_list_or_none([str, bytes], P) == (
        Concatenate[str, bytes, P])
