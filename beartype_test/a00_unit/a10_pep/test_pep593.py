#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** :pep:`593` **unit tests.**

This submodule unit tests :pep:`593` support implemented in the
:func:`beartype.beartype` decorator.
'''

# ....................{ IMPORTS                           }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                             }....................
def test_die_unless_hint_pep593() -> None:
    '''
    Test the
    :beartype._util.hint.pep.proposal.utilpep593.die_unless_hint_pep593`
    validator.
    '''

    # Defer heavyweight imports.
    from beartype.roar import BeartypeDecorHintPep593Exception
    from beartype._util.hint.pep.proposal.utilpep593 import (
        die_unless_hint_pep593)
    from beartype_test.util.mod.pytmodimport import (
        import_module_typing_any_attr_or_none_safe)
    from pytest import raises
    from typing import Optional

    # "typing.Annotated" type hint factory imported from either the "typing" or
    # "typing_extensions" modules if importable *OR* "None" otherwise.
    Annotated = import_module_typing_any_attr_or_none_safe('Annotated')

    # If this factory exists, assert this validator avoids raising exceptions
    # for a type hint subscripting this factory.
    if Annotated is not None:
        die_unless_hint_pep593(Annotated[Optional[str], int])

    # Assert this validator raises the expected exception for an arbitrary
    # PEP-compliant type hint *NOT* subscripting this factory.
    with raises(BeartypeDecorHintPep593Exception):
        die_unless_hint_pep593(Optional[str])
