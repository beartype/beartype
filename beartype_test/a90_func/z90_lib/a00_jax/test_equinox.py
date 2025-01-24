#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Equinox integration tests.**

This submodule functionally tests the :mod:`beartype` package against the
third-party :mod:`equinox` package.
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
from beartype_test._util.mark.pytskip import skip

# ....................{ TESTS                              }....................
def test_equinox_filter_jit() -> None:
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
    #See similar logic in "test_jax" also requiring a similar resolution.
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
        is_package('equinox', is_warnings_ignore=True) and
        is_package('jax', is_warnings_ignore=True) and
        is_package('jaxtyping', is_warnings_ignore=True)
    ):
        return
    # Else, all requisite JAX packages is importable.

    # ....................{ IMPORTS ~ late                 }....................
    # Defer JAX-dependent imports.
    from equinox import filter_jit
    from jax import numpy as jax_numpy
    from jaxtyping import (
        Array,
        Float,
    )

    # ....................{ LOCALS                         }....................
    # Type hint matching a JAX array of floating-point numbers.
    JaxArrayOfFloats = Float[Array, '']

    # JAX array of arbitrary floating-point numbers.
    of_those_beloved_eyes = jax_numpy.array(1.0)

    # ....................{ CALLABLES                      }....................
    @beartype
    @filter_jit
    def as_if_their_genii(
        were_the_ministers: JaxArrayOfFloats) -> JaxArrayOfFloats:
        '''
        Arbitrary callable decorated first by :func:`equinox.filter_jit` and
        then by :func:`beartype.beartype`, exercising a well-known edge case.
        '''

        # Do it because it feels good, one-liner.
        return were_the_ministers + 1


    @beartype
    @filter_jit
    def appointed_to_conduct_him(
        to_the_light: JaxArrayOfFloats) -> JaxArrayOfFloats:
        '''
        Arbitrary callable decorated first by :func:`equinox.filter_jit` and
        then by :func:`beartype.beartype`, exercising a well-known edge case.

        Note that fully exercising this edge case requires defining not merely
        one but *TWO* callables decorated in this order. Before this issue was
        resolved, :func:`beartype.beartype` *literally* swapped the code objects
        of these two callables. Believe it or not, it's beartype! O_o
        '''

        # Do it because it feels right, one-liner.
        return to_the_light - 1

    # ....................{ PASS                           }....................
    # Assert that these callables return the expected values when passed valid
    # parameters satisfying the type hints annotating these callables.
    assert as_if_their_genii(of_those_beloved_eyes) == (
        jax_numpy.array(2.0))
    assert appointed_to_conduct_him(of_those_beloved_eyes) == (
        jax_numpy.array(0.0))

    # ....................{ FAIL                           }....................
    # Assert that these callables raise the expected exceptions when passed
    # invalid parameters violating the type hints annotating these callables.
    with raises(BeartypeCallHintParamViolation):
        as_if_their_genii('Appointed to conduct him to the light')
    with raises(BeartypeCallHintParamViolation):
        appointed_to_conduct_him('Of those belovèd eyes, the Poet sate')


#FIXME: Resurrect this test *AFTER* resurrecting Equinox integration, please.
@skip('Currently broken due to @beartype temporarily dropping Equinox support.')
def test_equinox_module_subclass() -> None:
    '''
    Functional test validating that the :mod:`beartype` package successfully
    type-checks subclasses of superclasses defined by the third-party Equinox
    package annotated by type hints by the third-party :mod:`jaxtyping` package.

    See Also
    --------
    https://github.com/patrick-kidger/equinox/issues/584
        Upstream Equinox issue strongly inspiring this functional test.
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
    #See similar logic in "test_jax" also requiring a similar resolution.
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
        is_package('equinox', is_warnings_ignore=True) and
        is_package('jax', is_warnings_ignore=True) and
        is_package('jaxtyping', is_warnings_ignore=True)
    ):
        return
    # Else, all requisite JAX packages is importable.

    # ....................{ IMPORTS ~ late                 }....................
    # Defer JAX-dependent imports.
    from equinox import Module
    from jax import numpy as jax_numpy
    from jaxtyping import (
        Array,
        Float,
    )

    # ....................{ CLASSES                        }....................
    @beartype
    class EquinoxModule(Module):
        '''
        Arbitrary subclass of the :class:`equinox.Module` superclass decorated
        by the :func:`beartype.beartype` decorator.
        '''

        # ....................{ CLASS VARS                 }....................
        float_array: Float[Array, '']
        '''
        Arbitrary class variable annotated by a :mod:`jaxtyping` type hint.
        '''

        # ....................{ METHODS                    }....................
        def munge_array(self, python_bool: bool) -> Float[Array, '']:
            '''
            Arbitrary method accepting a trivial object to be type-checked.
            '''

            # Arbitrary one-liner is arbitrary.
            return self.float_array + 1

    # ....................{ LOCALS                         }....................
    # JAX-based NumPy array containing arbitrary data.
    jax_array = jax_numpy.array(1.0)

    # Arbitrary instance of the above Equinox subclass.
    equinox_module = EquinoxModule(jax_array)

    # ....................{ FAIL                           }....................
    # Assert that this @beartype-decorated method of this Equinox instance
    # raises the expected type-checking violation exception when passed an
    # invalid parameter violating the type hint annotating that parameter.
    with raises(BeartypeCallHintParamViolation):
        equinox_module.munge_array('A string is not a boolean.')
