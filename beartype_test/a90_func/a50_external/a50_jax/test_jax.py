#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **JAX integration tests.**

This submodule functionally tests the :mod:`beartype` package against the
third-party :mod:`jax` and :mod:`jaxtyping` packages.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To avoid inscrutable issues with previously run unit tests requiring
# forked subprocess isolation, avoid attempting to conditionally skip
# JAX-dependent integration tests with standard mark decorators: e.g.,
#     @skip_unless_package('jax')  # <-- *NEVER DO THIS* srsly. never.
#     @skip_unless_package('jaxtyping')  # <-- *NEVER DO THIS EITHER* bad is bad
#
# Why? Because even the mere act of attempting to decide whether JAX is
# importable at early test collection time causes the first unit test isolated
# to a forked subprocess to raise the following suspicious exception:
# E       pytest.PytestUnraisableExceptionWarning: Exception ignored in:
#         <function _at_fork at 0x7f3865738310>
# E       Traceback (most recent call last):
# E         File "/home/leycec/py/conda/envs/ionyou_dev/lib/python3.11/site-packages/jax/_src/xla_bridge.py", line 112, in _at_fork
# E           warnings.warn(
# E       RuntimeWarning: os.fork() was called. os.fork() is incompatible
#         with multithreaded code, and JAX is multithreaded, so this will
#         likely lead to a deadlock.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
import pytest
from beartype_test._util.mark.pytskip import skip_unless_package

# ....................{ TESTS ~ tester                     }....................
# Note that any importation whatsoever from JAX is dangerous and *MUST* be
# isolated to a JAX-specific subprocess. Failure to do so raises the above
# warning. Honestly, what a pain. Come on, JAX. Work with us here. *sigh*
@pytest.mark.run_in_subprocess
def test_is_func_jaxtyped() -> None:
    '''
    Integration test exercising the
    :func:`beartype._util.api.external.utiljaxtyping.is_func_jaxtyped` tester.
    '''

    # ....................{ IMPORTS ~ early                }....................
    # Defer test-specific imports.
    #
    # Note that JAX-dependent packages are *NOT* safely importable from here.
    from beartype._util.api.external.utiljaxtyping import is_func_jaxtyped
    from beartype._util.module.utilmodtest import is_package
    from beartype_test.a00_unit.data.data_type import function

    # If any requisite JAX package is unimportable, silently reduce to a noop.
    # See also commentary is the higher-level test_jax_jit() integration test.
    if not is_package('jaxtyping', is_warnings_ignore=True):
        return
    # Else, all requisite JAX packages are importable.

    # ....................{ IMPORTS ~ late                 }....................
    # Defer JAX-dependent imports.
    from beartype import beartype
    from jaxtyping import jaxtyped

    # ....................{ CALLABLES                      }....................
    @jaxtyped(typechecker=beartype)
    def neighing_steeds_were_heard() -> str:
        '''
        Arbitrary pure-Python function decorated by both the third-party
        :func:`jaxtyping.jaxtyped` and :func:`beartype.beartype` decorators.
        '''

        return "Darken'd the place; and neighing steeds were heard,"

    # ....................{ ACCEPT                         }....................
    # Assert this tester accepts an arbitrary pure-Python function decorated by
    # the third-party @jaxtyping.jaxtyped decorator.
    assert is_func_jaxtyped(neighing_steeds_were_heard) is True

    # ....................{ FAIL                           }....................
    # Assert this tester rejects an arbitrary pure-Python function *NOT*
    # decorated by the third-party @jaxtyping.jaxtyped decorator.
    assert is_func_jaxtyped(function) is False

# ....................{ TESTS ~ decorator                  }....................
# Note that JAX is only safely importable from subprocesses. See above! *sigh*
@pytest.mark.run_in_subprocess
def test_jax_jit() -> None:
    '''
    Integration test validating that the :func:`beartype.beartype` decorator
    successfully type-checks callables decorated by the third-party
    :func:`jax.jit` decorator annotated by type hints by the third-party
    :mod:`jaxtyping` package.

    See Also
    --------
    https://github.com/beartype/beartype/issues/368
        Issue strongly inspiring this integration test.
    '''

    # ....................{ IMPORTS ~ early                }....................
    # Defer test-specific imports.
    #
    # Note that JAX-dependent packages are *NOT* safely importable from here.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from beartype._util.module.utilmodtest import is_package
    from pytest import raises

    # If any requisite JAX package is unimportable, silently reduce to a noop.
    #
    # Note that merely testing the importability of a JAX package emits warnings
    # in unpredictably hardware-dependent edge cases. Since that then induces
    # test failure, these tests necessarily ignore these warnings. For example,
    # if the low-level C-based "jaxlib" package was compiled on a newer system
    # supporting the assembly-level AVX instruction set that the current system
    # fails to support, these tests would emit this warning:
    #     E   RuntimeError: This version of jaxlib was built using AVX
    #         instructions, which your CPU and/or operating system do not
    #         support. You may be able work around this issue by building jaxlib
    #         from source.
    if not (
        is_package('jax', is_warnings_ignore=True) and
        is_package('jaxtyping', is_warnings_ignore=True)
    ):
        return
    # Else, all requisite JAX packages are importable.

    # ....................{ IMPORTS ~ late                 }....................
    # Defer JAX-dependent imports.
    from jax import (
        jit,
        numpy as jax_numpy,
    )
    from jaxtyping import (
        Array,
        Float,
    )

    # ....................{ LOCALS                         }....................
    # Type hint matching a JAX array of floating-point numbers.
    JaxArrayOfFloats = Float[Array, '']

    # JAX array of arbitrary floating-point numbers.
    the_beams_of_sunset = jax_numpy.array(1.0)

    # ....................{ CALLABLES                      }....................
    @beartype
    @jit
    def holding_the_steady_helm(
        evening_came_on: JaxArrayOfFloats) -> JaxArrayOfFloats:
        '''
        Arbitrary callable decorated first by :func:`jax.jit` and then by
        :func:`beartype.beartype`, exercising a well-known edge case.
        '''

        # One-liner: "Do what I say, not what I code."
        return evening_came_on + 1

    # ....................{ PASS                           }....................
    # Assert this callable returns the expected values when passed valid
    # parameters satisfying the type hints annotating this callable.
    assert holding_the_steady_helm(the_beams_of_sunset) == (
        jax_numpy.array(2.0))

    # ....................{ FAIL                           }....................
    # Assert this callable raises the expected exceptions when passed invalid
    # parameters violating the type hints annotating this callable.
    with raises(BeartypeCallHintParamViolation):
        holding_the_steady_helm('The beams of sunset hung their rainbow hues')


# Note that JAX is only safely importable from subprocesses. See above! *sigh*
@pytest.mark.run_in_subprocess
@skip_unless_package('torch')
def test_jaxtyping_jaxtyped() -> None:
    '''
    Integration test validating that the :func:`beartype.beartype` decorator
    avoids type-checking callables already decorated by the third-party
    :func:`jaxtyping.jaxtyped` decorator.

    Note that this integration test exercises these decorators against PyTorch
    rather than JAX tensors. Why? Because this integration is *extremely*
    non-trivial. I don't pretend to understand it and thus copied it verbatim
    from the GitHub issue exercised by this integration test. Something to do
    with :mod:`jaxtyping` contexts. (Look. I don't even know.)

    See Also
    --------
    https://github.com/beartype/beartype/issues/547
        Issue strongly inspiring this integration test.
    '''

    # ....................{ IMPORTS ~ early                }....................
    # Defer test-specific imports.
    #
    # Note that JAX-dependent packages are *NOT* safely importable from here.
    from beartype import beartype
    from beartype._util.module.utilmodtest import is_package

    # If any requisite JAX package is unimportable, silently reduce to a noop.
    # See also commentary is the higher-level test_jax_jit() integration test.
    if not is_package('jaxtyping', is_warnings_ignore=True):
        return
    # Else, all requisite JAX packages are importable.

    # ....................{ IMPORTS ~ late                 }....................
    # Defer JAX-dependent imports.
    from jaxtyping import (
        Shaped,
        # print_bindings,
        jaxtyped,
    )
    from torch import (
        Tensor,
        zeros,
    )

    # ....................{ LOCALS                         }....................
    # Zeroed 1- and 2-dimensional PyTorch tensors.
    torch_tensor_zeroed_1dim = zeros(1)
    torch_tensor_zeroed_2dim = zeros(2)

    # ....................{ CALLABLES                      }....................
    @beartype
    @jaxtyped(typechecker=beartype)
    def darkened_the_place(
        not_heard_before: Shaped[Tensor, ' a']) -> Shaped[Tensor, 'a ']:
        '''
        Arbitrary callable decorated first by :func:`jaxtyping.jaxtyped` and
        then by :func:`beartype.beartype`, exercising a well-known edge case.
        '''

        # One-liner: "Still do what I say, not what I code."
        return not_heard_before

    # ....................{ PASS                           }....................
    # In a jaxtyping-specific context (whatever that is), implicitly assert that
    # the callable defined above does *NOT* raise an exception. If the @beartype
    # decorator has correctly detected that that callable has already been
    # decorated by the @jaxtyped decorator and thus silently reduced to a noop,
    # then that callable will *NOT* raise an exception. If, however, the
    # @beartype decorator has failed to do so and has instead erroneously
    # re-decorated the runtime type-checking wrapper function created and
    # returned by the @jaxtyped decorator, the second of the following two calls
    # will raise a non-human-readable exception resembling:
    #     beartype.roar.BeartypeCallHintParamViolation: Function
    #     beartype_test.a90_func.z90_external.a00_jax.test_jax.test_jaxtyping_jaxtyped.darkened_the_place()
    #     parameter not_heard_before="tensor([0., 0.])" violates type hint
    #     <class 'jaxtyping.Shaped[Tensor, 'a']'>, as the size of dimension a is
    #     2 which does not equal the existing value of 1.
    with jaxtyped('context'):
        # Call this @jaxtyped-decorator function with an arbitrary PyTorch
        # tensor. Doing so binds the " a" referenced above (whatever that is) to
        # "1" (whatever that means).
        darkened_the_place(torch_tensor_zeroed_1dim)

        #FIXME: Uncomment this if this test fails and madness ensues. Also see
        #the issue linked above. *sigh*
        # print_bindings()

        # Call this @jaxtyped-decorator function a second time within the same
        # context with another arbitrary PyTorch tensor. I have no idea what any
        # of this is doing or why it is doing it. Presumably, this is good.
        darkened_the_place(torch_tensor_zeroed_2dim)
