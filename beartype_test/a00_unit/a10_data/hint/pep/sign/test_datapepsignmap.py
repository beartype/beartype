#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **type hint sign mapping** unit tests.

This submodule unit tests the public API of the private
:mod:`beartype._data.hint.pep.sign.datapepsignmap` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS                              }....................
def test_hint_sign_origin_isinstanceable_to_args_len_range() -> None:
    '''
    Test the
    :obj:`beartype._data.hint.pep.sign.datapepsignmap.HINT_SIGN_ORIGIN_ISINSTANCEABLE_TO_ARGS_LEN_RANGE`
    dictionary global.

    This test guarantees conformance between this global and the corresponding
    type hint factories published by the standard :mod:`typing` module.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    import typing
    from beartype._data.hint.pep.sign.datapepsigns import HintSignTuple
    from beartype._data.hint.pep.sign.datapepsignmap import (
        HINT_SIGN_ORIGIN_ISINSTANCEABLE_TO_ARGS_LEN_RANGE)

    # ....................{ ASSERTS                        }....................
    # For each sign uniquely identifying an official type hint factory
    # subscriptable by a known number of child type hints and a "range" object
    # describing that number...
    for hint_sign, args_len_range in (
        HINT_SIGN_ORIGIN_ISINSTANCEABLE_TO_ARGS_LEN_RANGE.items()):
        # print(f'Inspecting {args_len_belief}-argument sign {args_sign}...')

        # If this is the sign uniquely identifying fixed-length tuple type hints
        # (e.g., "tuple[int, str]"), silently ignore the corresponding
        # "typing.Tuple" type hint factory and proceed to the next sign. Why?
        # Because that factory ambiguously supports both fixed- and variable-
        # length tuple type hints and thus defines:
        #     >>> from typing import Tuple
        #     >>> Tuple._nparams
        #     -1
        #
        # Needless to say, "-1" is an invalid number of arguments. *sigh*
        if hint_sign is HintSignTuple:
            return
        # Else, this is *NOT* the sign uniquely identifying fixed-length tuple
        # type hints.

        # Type hint factory published by the "typing" module with this name.
        hint_factory = getattr(typing, hint_sign.name)

        # Maximum number of arguments believed to be accepted by this factory
        # according to this dictionary.
        #
        # Note that the "stop" instance variable defined by "range" objects is
        # exclusive rather than inclusive. Substracting 1 from that yields the
        # inclusive maximum of this range.
        ARGS_LEN_MAX_BELIEF = args_len_range.stop - 1

        # Maximum number of arguments actually accepted by this factory.
        # Thankfully, this factory conveniently defines a private "_nparams"
        # instance variable providing this maximum number.
        ARGS_LEN_MAX_ACTUAL: int = hint_factory._nparams

        # Assert that these numbers of arguments correspond.
        assert ARGS_LEN_MAX_BELIEF == ARGS_LEN_MAX_ACTUAL, (
            f'Type hint factory "typing.{hint_sign.name}" accepts a maximum of '
            f'{ARGS_LEN_MAX_ACTUAL} child type hints but expected to accept a maximum of '
            f'{ARGS_LEN_MAX_BELIEF} child type hints.'
        )
