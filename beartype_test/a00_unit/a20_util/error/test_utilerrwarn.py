#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype exception raiser utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.error.utilerrwarn` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_reissue_warnings_placeholder() -> None:
    '''
    Test the
    :func:`beartype._util.error.utilerrwarn.reissue_warnings_placeholder`
    function.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype._util.error.utilerrwarn import (
        issue_warning,
        reissue_warnings_placeholder,
    )
    from pytest import warns
    from warnings import catch_warnings

    # ....................{ CLASSES                        }....................
    class TheSkyWarning(UserWarning):
        '''
        Arbitrary warning issued below with messages containing placeholder
        substrings replaced by :func:`.reissue_warnings_placeholder`.
        '''

        pass


    class ThePoetWarning(UserWarning):
        '''
        Arbitrary warning issued below with messages containing placeholder
        substrings replaced by :func:`.reissue_warnings_placeholder`.
        '''

        pass

    # ....................{ LOCALS                         }....................
    # Source substring to be hard-coded into the messages of all warnings
    # issued by the low-level callable defined below.
    TEST_SOURCE_STR = '{its_got_bro}'

    # Target substring to globally replace this source substring with.
    TEST_TARGET_STR = 'With his still soul. '

    # ....................{ CALLABLES                      }....................
    def portend_his_brain() -> None:
        '''
        Low-level callable issuing two or more possibly unreadable warnings.
        '''

        # Issue an arbitrary warning message containing one source substring.
        issue_warning(
            cls=TheSkyWarning,
            message=f'{TEST_SOURCE_STR}The sky',
        )

        # Issue an arbitrary warning message containing *NO* source substring.
        issue_warning(
            cls=ThePoetWarning,
            message='the Poet kept mute conference',
        )

        # Issue an empty warning message.
        issue_warning(cls=TheSkyWarning, message='')

        # Issue a non-string warning message. While an unlikely edge case, the
        # standard low-level warnings.warn() function permissively permits this.
        # Moreover, this behaviour coincides with similar permissiveness in
        # exception messages (which are also allowed to be non-strings): e.g.,
        #     >>> from warnings import warn
        #     >>> warn(0xCAFE, UserWarning)
        #     UserWarning: 51966
        #       warn(0xCAFE, UserWarning)
        issue_warning(cls=ThePoetWarning, message=0xBEEFDEAD)


    def portend_while_daylight() -> None:
        '''
        High-level callable calling the low-level callable and reissuing
        unreadable warnings issued by the latter with equivalent readable
        warnings.
        '''

        # With a context manager "catching" *ALL* non-fatal warnings emitted
        # during this logic for subsequent "playrback" below...
        with catch_warnings(record=True) as warnings_issued:
            # Call this low-level callable to emit multiple warnings.
            portend_his_brain()

        # If one or more warnings were issued, reissue these warnings with each
        # placeholder substring replaced by an arbitrary substring.
        if warnings_issued:
            reissue_warnings_placeholder(
                warnings=warnings_issued,
                source_str=TEST_SOURCE_STR,
                target_str=TEST_TARGET_STR,
            )
        # Else, *NO* warnings were issued.

    # ....................{ ASSERT                         }....................
    # Assert this high-level non-memoized callable raises the same type of
    # exception raised by this low-level memoized callable and preserve this
    # exception for subsequent assertion.
    #
    # Note that passing nothing to warns() enables undocumented edge-case
    # behaviour in which warns() captures warnings issued by this block
    # *WITHOUT* validating the types of these warnings. See also:
    #     https://docs.pytest.org/en/4.6.x/warnings.html#recwarn
    with warns() as warnings_info:
        portend_while_daylight()

    # Assert that the expected number of warnings were issued.
    assert len(warnings_info) == 4

    # Assert that the expected types of warnings were issued.
    assert issubclass(warnings_info[0].category, TheSkyWarning)
    assert issubclass(warnings_info[1].category, ThePoetWarning)
    assert issubclass(warnings_info[2].category, TheSkyWarning)
    assert issubclass(warnings_info[3].category, ThePoetWarning)

    # Assert that the expected warning messages were issued.
    assert str(warnings_info[0].message) == f'{TEST_TARGET_STR}The sky'
    assert str(warnings_info[1].message) == 'the Poet kept mute conference'
    assert str(warnings_info[2].message) == ''
    assert warnings_info[3].message.args == (0xBEEFDEAD,)
