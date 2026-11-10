#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype :pep:`593` unit tests.

This submodule unit tests :pep:`593` support implemented in the
:func:`beartype.beartype` decorator.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_decor_pep593_mixed() -> None:
    '''
    Test that the :func:`beartype.beartype` decorator and
    :func:`beartype.door.is_bearable` function silently ignore beartype-agnostic
    metadata intermingled with beartype validators subscripting :pep:`593`-
    compliant metahints.
    '''

    # Defer test-specific imports.
    from beartype import beartype
    from beartype.door import is_bearable
    from beartype.roar import BeartypeCallHintParamViolation
    from beartype.vale import Is
    from beartype._util.api.standard.utiltyping import get_typing_attrs
    from pytest import raises

    # Arbitrary beartype-agnostic metadata, resembling "annotated_types.MaxLen".
    class MaxLen(object):
        def __init__(self, max_length: int) -> None:
            self.max_length = max_length

    IsShort = Is[lambda obj: len(obj) <= 1]

    # For the "Annotated" type hint factory exported by each typing module...
    for Annotated in get_typing_attrs('Annotated'):
        # Validators preceding, following, and surrounded by agnostic metadata.
        for hint in (
            Annotated[list[int], IsShort, MaxLen(1)],
            Annotated[list[int], MaxLen(1), IsShort],
            Annotated[list[int], 'a', IsShort, MaxLen(1), 'b'],
            Annotated[Annotated[list[int], MaxLen(1)], IsShort],
        ):
            assert is_bearable([1], hint) is True
            assert is_bearable([1, 2], hint) is False
            assert is_bearable(['a'], hint) is False

        @beartype
        def volleyed_and_thundered(
            flashed: Annotated[str, Is[lambda text: len(text) > 2], 'x'],
        ) -> str:
            return flashed

        assert volleyed_and_thundered('abc') == 'abc'
        with raises(BeartypeCallHintParamViolation):
            volleyed_and_thundered('a')
