#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Call stack utility unit tests.**

This submodule unit tests the public API of the private
:mod:`beartype._util.utilfunc.utilfuncframe` submodule.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# ....................{ TESTS ~ getters                    }....................
def test_get_frame() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfuncframe.get_frame` getter.
    '''

    # Defer test-specific imports.
    from beartype._util.func.utilfuncframe import get_frame

    # Assert this attribute is a callable under both CPython and PyPy.
    assert callable(get_frame) is True

# ....................{ TESTS ~ iterators                  }....................
def test_iter_frames() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfuncframe.iter_frames` iterator.
    '''

    # Defer test-specific imports.
    from beartype._util.func.utilfunccodeobj import get_func_codeobj
    from beartype._util.func.utilfuncframe import iter_frames

    # For each stack frame on the current call stack iterated by this
    # iterator...
    for frame in iter_frames():
        # Code object underlying the pure-Python function encapsulated by this
        # stack frame.
        frame_codeobj = get_func_codeobj(frame)

        # Unqualified name of this function.
        frame_name = frame_codeobj.co_name

        # Assert that this function is the current unit test function.
        assert frame_name == 'test_iter_frames'

        # Halt iteration. For safety, avoid attempting to assert *ANYTHING*
        # about pytest-specific stack frames deeper in the call stack.
        break
    # If the prior "break" statement was *NOT* run, the prior iteration did
    # *NOT* run at all. In this case, raise an unconditional test failure.
    else:
        assert False, 'iter_frames() empty.'

    # Assert that this iterator reduces to the empty generator when asked to
    # ignore more stack frames than currently reside on the call stack.
    #
    # Note that an excessively large number of stack frames is intentionally
    # chosen to avoid conflicts with "pytest" itself, which is implemented in
    # pure-Python and thus runs tests with Python functions that themselves add
    # an arbitrary number of stack frames to the call stack.
    assert tuple(iter_frames(func_stack_frames_ignore=999999)) == ()
