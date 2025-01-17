#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **JAX integration tests.**

This submodule functionally tests the :mod:`beartype` package against the
third-party :mod:`jax` package.
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

# ....................{ TESTS                              }....................
def test_jax_jit() -> None:
    '''
    Functional test validating that the :mod:`beartype` package successfully
    type-checks callables decorated by the third-party
    :func:`equinox.filter_jit` decorator annotated by type hints by the
    third-party :mod:`jaxtyping` package.

    See Also
    --------
    https://github.com/beartype/beartype/issues/368
        Issue strongly inspiring this functional test.
    '''

    # ....................{ IMPORTS ~ early                }....................
    # Defer test-specific imports.
    #
    # Note that JAX-dependent packages are *NOT* safely importable from here.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from beartype._util.module.utilmodtest import is_package
    from pytest import raises

    #FIXME: *EVEN THIS ISN"T SAFE.* Any importation whatsoever from JAX is
    #dangerous and *MUST* be isolated to a subprocess. Honestly, what a pain.
    #See similar logic in "test_equinox" also requiring a similar resolution.
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
    # Else, all requisite JAX packages is importable.

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
    # Assert that these callables return the expected values when passed valid
    # parameters satisfying the type hints annotating these callables.
    assert holding_the_steady_helm(the_beams_of_sunset) == (
        jax_numpy.array(2.0))

    # ....................{ FAIL                           }....................
    # Assert that these callables raise the expected exceptions when passed
    # invalid parameters violating the type hints annotating these callables.
    with raises(BeartypeCallHintParamViolation):
        holding_the_steady_helm('The beams of sunset hung their rainbow hues')
