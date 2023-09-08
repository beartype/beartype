#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype decorator :pep:`577` unit tests.

This submodule unit tests :pep:`577` support implemented in the
:func:`beartype.beartype` decorator.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_decor_pep577() -> None:
    '''
    Test :pep:`557` support implemented in the :func:`beartype.beartype`
    decorator if the active Python interpreter targets Python >= 3.8 *or* skip
    otherwise.
    '''

    # ..................{ IMPORTS                            }..................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from beartype.typing import (
        ClassVar,
        Optional,
    )
    from dataclasses import (
        InitVar,
        dataclass,
        field,
    )
    from pytest import raises

    # ..................{ LOCALS                             }..................
    @beartype
    @dataclass
    class SoSolemnSoSerene(object):
        '''
        Arbitrary dataclass type-checked by :func:`beartype.beartype`.
        '''

        # Non-field instance variable passed by the @dataclass decorator to
        # both this __init__() method *AND* the explicit __post_init__() method
        # defined below.
        #
        # Note this mandatory parameter *MUST* be declared before all optional
        # parameters due to inscrutable issues in the @dataclass decorator.
        # Notably, @dataclass refuses to correctly reorder parameters. *sigh*
        but_for_such_faith: InitVar[str]

        # Standard instance variable passed by the @dataclass decorator to the
        # the implicit __init__() method synthesized for this class.
        that_man_may_be: Optional[str] = None

        # Uninitialized instance variable *NOT* passed by the @dataclass
        # decorator to this __init__() method.
        thou_hast_a_voice: int = field(default=0xBABE, init=False)

        # Class variable ignored by the @dataclass decorator and thus *NOT*
        # passed to this __init__() method.
        with_nature_reconciled: ClassVar[bool] = True

        @beartype
        def __post_init__(self, but_for_such_faith: str) -> None:
            '''
            :func:`dataclasses.dataclass`-specific dunder method implicitly
            called by the :meth:`__init__` method synthesized for this class,
            explicitly type-checked by :func:`beartype.beartype` for testing.
            '''

            if self.that_man_may_be is None:
                self.that_man_may_be = but_for_such_faith

    # Arbitrary instance of this dataclass exercising all edge cases.
    great_mountain = SoSolemnSoSerene(
        but_for_such_faith='So solemn, so serene, that man may be,')

    # ..................{ PASS                               }..................
    # Assert this dataclass defines the expected attributes.
    assert great_mountain.that_man_may_be == (
        'So solemn, so serene, that man may be,')
    assert great_mountain.thou_hast_a_voice == 0xBABE
    assert great_mountain.with_nature_reconciled == True

    # Assert this dataclass defines *NO* unexpected attributes.
    assert not hasattr(great_mountain, 'but_for_such_faith')

    # ..................{ FAIL                               }..................
    # Assert that attempting to instantiate an instance of this dataclass with a
    # parameter violating the corresponding type hint annotating the field of
    # the same name raises the expected exception.
    with raises(BeartypeCallHintParamViolation):
        SoSolemnSoSerene(but_for_such_faith=0xBEEFBABE)
