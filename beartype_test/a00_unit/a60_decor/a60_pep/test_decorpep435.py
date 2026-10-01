#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2026 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype decorator :pep:`435`-compliant enumeration unit tests.

This submodule unit tests :pep:`435` support for enumerations implemented in the
:func:`beartype.beartype` decorator.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_decor_pep435_subclass_nested() -> None:
    '''
    Test :pep:`435`-compliant **enumeration subclasses** (i.e.,
    :class:`enum.Enum` subclasses) decorated by the :func:`beartype.beartype`
    decorator and nested inside arbitrary other classes.

    See Also
    --------
    https://github.com/beartype/beartype/issues/707
        Outer class instantiation exercised by this unit test.
    https://github.com/beartype/beartype/issues/710
        Outer class namespace mutation exercised by this unit test.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from enum import Enum
    from beartype_test._util.error.pyterrraise import raises_uncached

    # ....................{ LOCALS                         }....................
    class ForOneShortHour(object):
        '''
        Arbitrary class defining a :pep:`435`-compliant **nested enumeration
        subclasses** (i.e., :class:`enum.Enum` subclass).
        '''

        THAT_WHISPER_ROUND = 'outer value'

        @beartype
        class EvenAsTheTrees(Enum):
            '''
            :pep:`435`-compliant **nested enumeration subclass** (i.e.,
            :class:`enum.Enum` subclass nested inside another arbitrary class).
            '''

            THAT_WHISPER_ROUND = 3
            '''
            Arbitrary integer-style enumeration member referenced below.
            '''

            def a_temple(self, become_soon: 'str') -> str:
                '''
                Arbitrary method annotated by an arbitrary :pep:`484`-compliant
                stringified forward reference.
                '''

                return 'That whisper round a temple ' + become_soon

    # ....................{ LOCALS                         }....................
    # Arbitrary integer-style enumeration member referenced below, intentionally
    # looked up by integer access against this nested enumeration subclass.
    THAT_WHISPER_ROUND = ForOneShortHour.EvenAsTheTrees(3)

    # ....................{ PASS                           }....................
    # Assert that the outer class defined above is instantiable. You are now
    # thinking: "Uh. Why wouldn't it be?" Because issue #707. Please don't ask.
    assert isinstance(ForOneShortHour(), ForOneShortHour)

    # Assert that the @beartype decorator preserved (rather than erroneously
    # overwriting) the namespace of the outer class defined above when it
    # internally resolved the PEP 484-compliant forward reference annotating the
    # method defined on the inner enumeration contained inside that outer class.
    assert ForOneShortHour.THAT_WHISPER_ROUND == 'outer value'
    assert ForOneShortHour.__new__ is object.__new__
    assert ForOneShortHour.__dict__.get('a_temple') is None
    assert ForOneShortHour.__dict__.get('_member_map_') is None

    # Assert that the method defined above returns the expected value when
    # passed a valid value.
    assert THAT_WHISPER_ROUND.a_temple('become soon') == (
        'That whisper round a temple become soon')

    # ....................{ FAIL                           }....................
    # Assert that the method defined above raises the expected exception when
    # passed an invalid value.
    with raises_uncached(BeartypeCallHintParamViolation):
        THAT_WHISPER_ROUND.a_temple(b'Ugh!')
