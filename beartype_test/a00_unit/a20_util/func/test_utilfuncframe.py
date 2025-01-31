#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
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
def test_get_frame_or_none() -> None:
    '''
    Test the
    :func:`beartype._util.func.utilfuncframe.get_frame_or_none` getter.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.roar._roarexc import _BeartypeUtilCallFrameException
    from beartype._util.func.utilfunccodeobj import get_func_codeobj
    from beartype._util.func.utilfuncframe import get_frame_or_none
    from pytest import raises
    from sys import maxsize

    # ....................{ CALLABLES                      }....................
    def while_fate() -> None:
        '''
        Arbitrary callable calling another callable calling another callable.
        '''

        seemd_strangled()


    def seemd_strangled() -> None:
        '''
        Arbitrary callable calling another callable.
        '''

        in_my_nervous_grasp()


    def in_my_nervous_grasp() -> None:
        '''
        Arbitrary callable calling *no* other callable but instead validating
        the stack frames on the current call stack are as expected.
        '''

        # ....................{ PASS                       }....................
        # Assert this getter returns the parent stack frame when passed *NO*
        # parameters.
        seemd_strangled_frame = get_frame_or_none()
        assert (
            get_func_codeobj(seemd_strangled_frame) is
            get_func_codeobj(seemd_strangled)
        )

        # Assert this getter returns the current stack frame when passed 0.
        in_my_nervous_grasp_frame = get_frame_or_none(0)
        assert (
            get_func_codeobj(in_my_nervous_grasp_frame) is
            get_func_codeobj(in_my_nervous_grasp)
        )

        # Assert this getter returns the parent parent stack frame when passed
        # 2.
        while_fate_frame = get_frame_or_none(2)
        assert (
            get_func_codeobj(while_fate_frame) is
            get_func_codeobj(while_fate)
        )

    # ....................{ PASS                           }....................
    # Call an arbitrary callable calling another callable calling another
    # callable validating the stack frames on the current call stack.
    while_fate()

    # Assert this getter returns "None" when the passed number of stack frames
    # to ignore is an absurdly large positive integer guaranteed to either:
    # * Trigger a C-based integer overflow.
    # * *NOT* trigger such an overflow but still exceed the total number of
    #   stack frames on the current call stack.
    assert get_frame_or_none(maxsize) is None  # <-- overflow!
    assert get_frame_or_none(9999) is None  # <-- no overflow!

    # ....................{ FAIL                           }....................
    # Assert this getter raises the expected exception when the passed number of
    # stack frames to ignore is *NOT* a non-negative integer.
    with raises(_BeartypeUtilCallFrameException):
        get_frame_or_none("While Fate seem'd strangled in my nervous grasp?")
    with raises(_BeartypeUtilCallFrameException):
        get_frame_or_none(-1)


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
