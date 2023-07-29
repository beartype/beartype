#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype** :pep:`593` **utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.hint.pep.proposal.utilpep593` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ validators                 }....................
def test_die_unless_hint_pep593() -> None:
    '''
    Test the
    :beartype._util.hint.pep.proposal.utilpep593.die_unless_hint_pep593`
    validator.
    '''

    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep593Exception
    from beartype._util.hint.pep.proposal.utilpep593 import (
        die_unless_hint_pep593)
    from beartype_test._util.module.pytmodtyping import (
        import_typing_attr_or_none_safe)
    from pytest import raises
    from typing import Optional

    # "typing.Annotated" type hint factory imported from either the "typing" or
    # "typing_extensions" modules if importable *OR* "None" otherwise.
    Annotated = import_typing_attr_or_none_safe('Annotated')

    # If this factory exists, assert this validator avoids raising exceptions
    # for a type hint subscripting this factory.
    if Annotated is not None:
        die_unless_hint_pep593(Annotated[Optional[str], int])

    # Assert this validator raises the expected exception for an arbitrary
    # PEP-compliant type hint *NOT* subscripting this factory.
    with raises(BeartypeDecorHintPep593Exception):
        die_unless_hint_pep593(Optional[str])

# ....................{ TESTS ~ tester                     }....................
def test_is_hint_pep593_beartype() -> None:
    '''
    Test usage of the private
    :mod:`beartype._util.hint.pep.proposal.utilpep593.is_hint_pep593_beartype`
    tester.
    '''

    # Defer test-specific imports.
    from beartype.roar import (
        BeartypeDecorHintPepException,
        BeartypeValeLambdaWarning,
    )
    from beartype.vale import Is
    from beartype._util.hint.pep.proposal.utilpep593 import (
        is_hint_pep593_beartype)
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
    from pytest import raises, warns

    # If the active Python interpreter targets at least Python >= 3.9 and thus
    # supports PEP 593...
    if IS_PYTHON_AT_LEAST_3_9:
        # Defer version-specific imports.
        from typing import Annotated

        # Assert this tester accepts beartype-specific metahints.
        #
        # Unfortunately, this test actually induces an error in CPython, which
        # our codebase emits as a non-fatal warning. Specifically, CPython
        # reports the "func.__code__.co_firstlineno" attribute of the nested
        # lambda function defined below to be one less than the expected value.
        # Since this issue is unlikely to be resolved soon *AND* since we have
        # no means of monkey-patching CPython itself, we acknowledge the
        # existence of this warning by simply ignoring it. *sigh*
        with warns(BeartypeValeLambdaWarning):
            assert is_hint_pep593_beartype(Annotated[
                str, Is[lambda text: bool(text)]]) is True

        # Assert this tester rejects beartype-agnostic metahints.
        assert is_hint_pep593_beartype(Annotated[
            str, 'And may there be no sadness of farewell']) is False

    # Assert this tester raises the expected exception when passed a
    # non-metahint in either case.
    with raises(BeartypeDecorHintPepException):
        is_hint_pep593_beartype('When I embark;')

# ....................{ TESTS ~ getters                    }....................
def test_get_hint_pep593_metadata() -> None:
    '''
    Test the
    :beartype._util.hint.pep.proposal.utilpep593.get_hint_pep593_metadata`
    getter.
    '''

    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep593Exception
    from beartype._util.hint.pep.proposal.utilpep593 import (
        get_hint_pep593_metadata)
    from beartype_test._util.module.pytmodtyping import (
        import_typing_attr_or_none_safe)
    from pytest import raises
    from typing import Optional

    # "typing.Annotated" type hint factory imported from either the "typing" or
    # "typing_extensions" modules if importable *OR* "None" otherwise.
    Annotated = import_typing_attr_or_none_safe('Annotated')

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

    # Defer test-specific imports.
    from beartype.roar import BeartypeDecorHintPep593Exception
    from beartype._util.hint.pep.proposal.utilpep593 import (
        get_hint_pep593_metahint)
    from beartype_test._util.module.pytmodtyping import (
        import_typing_attr_or_none_safe)
    from pytest import raises
    from typing import Optional

    # "typing.Annotated" type hint factory imported from either the "typing" or
    # "typing_extensions" modules if importable *OR* "None" otherwise.
    Annotated = import_typing_attr_or_none_safe('Annotated')

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
