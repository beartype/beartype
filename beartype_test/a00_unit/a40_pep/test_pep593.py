#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2022 Beartype authors.
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

# ....................{ TESTS ~ validators                }....................
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

# ....................{ TESTS ~ getters                   }....................
def test_get_hint_pep593_metadata() -> None:
    '''
    Test the
    :beartype._util.hint.pep.proposal.utilpep593.get_hint_pep593_metadata`
    getter.
    '''

    # Defer heavyweight imports.
    from beartype.roar import BeartypeDecorHintPep593Exception
    from beartype._util.hint.pep.proposal.utilpep593 import (
        get_hint_pep593_metadata)
    from beartype_test.util.mod.pytmodimport import (
        import_module_typing_any_attr_or_none_safe)
    from pytest import raises
    from typing import Optional

    # "typing.Annotated" type hint factory imported from either the "typing" or
    # "typing_extensions" modules if importable *OR* "None" otherwise.
    Annotated = import_module_typing_any_attr_or_none_safe('Annotated')

    # If this factory exists, assert this getter returns the expected tuple for
    # an arbitrary PEP 593-compliant type hint.
    if Annotated is not None:
        assert get_hint_pep593_metadata(Annotated[
            Optional[str],
            'Thy', 'caverns', 'echoing', 'to', 'the', "Arve's", 'commotion,'
        ]) == (
            'Thy', 'caverns', 'echoing', 'to', 'the', "Arve's", 'commotion,')

    # Assert this getter raises the expected exception for an arbitrary
    # PEP-compliant type hint *NOT* subscripting this factory.
    with raises(BeartypeDecorHintPep593Exception):
        get_hint_pep593_metadata(Optional[str])


def test_get_hint_pep593_metahint() -> None:
    '''
    Test the
    :beartype._util.hint.pep.proposal.utilpep593.get_hint_pep593_metahint`
    getter.
    '''

    # Defer heavyweight imports.
    from beartype.roar import BeartypeDecorHintPep593Exception
    from beartype._util.hint.pep.proposal.utilpep593 import (
        get_hint_pep593_metahint)
    from beartype_test.util.mod.pytmodimport import (
        import_module_typing_any_attr_or_none_safe)
    from pytest import raises
    from typing import Optional

    # "typing.Annotated" type hint factory imported from either the "typing" or
    # "typing_extensions" modules if importable *OR* "None" otherwise.
    Annotated = import_module_typing_any_attr_or_none_safe('Annotated')

    # If this factory exists, assert this getter returns the expected
    # PEP-compliant type hint for an arbitrary PEP 593-compliant type hint.
    if Annotated is not None:
        metahint = Optional[int]
        assert get_hint_pep593_metahint(Annotated[
            metahint,
            'A', 'loud', 'lone', 'sound', 'no', 'other', 'sound', 'can', 'tame'
        ]) is metahint

    # Assert this getter raises the expected exception for an arbitrary
    # PEP-compliant type hint *NOT* subscripting this factory.
    with raises(BeartypeDecorHintPep593Exception):
        get_hint_pep593_metahint(Optional[str])
