#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype type hint sign set unit tests.**

This submodule unit tests the public API of the public
:mod:`beartype._data.hint.pep.sign.datapepsignset` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ testers                    }....................
def test_hint_signs_origin_isinstanceable_args() -> None:
    '''
    Test all global frozen sets defined by the
    :mod:`beartype._data.hint.pep.sign.datapepsignset` submodule whose names are
    prefixed by ``"HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_"``.

    This test guarantees conformance between these sets and their corresponding
    type hint factories published by the :mod:`typing` module.
    '''

    # Defer test-specific imports.
    import typing
    from beartype._data.hint.pep.sign.datapepsignset import (
        HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_1,
        HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_2,
        HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_3,
    )
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9

    # Tuple of 2-tuples "(args_len, args_signs)", where:
    # * "args_len" is the number of arguments accepted by this kind of type hint
    #   factory originating from an isinstanceable origin type.
    # * "args_signs" is the set of all signs uniquely identifying type hint
    #   factories originating from an isinstanceable origin type which are
    #   subscriptable (i.e., indexable) by this number of arguments.
    ARGS_LEN_TO_SIGNS = (
        (1, HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_1),
        (2, HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_2),
        (3, HINT_SIGNS_ORIGIN_ISINSTANCEABLE_ARGS_3),
    )

    # For each number of arguments and set of signs uniquely identifying type
    # hint factories subscriptable by this number of arguments...
    for args_len_belief, args_signs in ARGS_LEN_TO_SIGNS:
        # For each such sign...
        for args_sign in args_signs:
            # Type hint factory published by the "typing" module with this name.
            args_factory = getattr(typing, args_sign.name)

            # Number of arguments actually accepted by this factory.
            args_len_actual = None

            # If the active Python interpreter targets Python >= 3.9, this
            # type hint factory conveniently defines a private "_nparams"
            # instance variable with this number.
            if IS_PYTHON_AT_LEAST_3_9:
                args_len_actual = args_factory._nparams
            # Else, this interpreter targets Python < 3.9. In this case, this
            # type hint factory instead defines a private "__args__" instance
            # variable providing the tuple of all "TypeVar" instances
            # constraining the arguments accepted by this factory.
            else:
                args_len_actual = len(args_factory.__args__)

            # Assert that these numbers of arguments correspond.
            assert args_len_belief == args_len_actual, (
                f'"typing.{args_sign.name}" accepts '
                f'{args_len_actual} arguments, but expected to accept '
                f'{args_len_belief} arguments.'
            )
