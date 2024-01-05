#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Equinox integration tests.**

This submodule functionally tests the :mod:`beartype` package against the
third-party Equinox package.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_unless_package

# ....................{ TESTS                              }....................
@skip_unless_package('equinox')
def test_equinox() -> None:
    '''
    Functional test validating that the :mod:`beartype` package successfully
    type-checks subclasses of superclasses defined by the third-party Equinox
    package annotated by type hints by the third-party :mod:`jaxtyping` package.

    See Also
    --------
    https://github.com/patrick-kidger/equinox/issues/584
        Upstream Equinox issue strongly inspiring this functional test.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from beartype.roar import BeartypeCallHintParamViolation
    from equinox import Module
    from jax import numpy as jnp
    from jaxtyping import (
        Array,
        Float,
    )
    from pytest import raises

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
    jax_array = jnp.array(1.)

    # Arbitrary instance of the above Equinox subclass.
    equinox_module = EquinoxModule(jax_array)

    # ....................{ FAIL                           }....................
    # Assert that this @beartype-decorated method of this Equinox instance
    # raises the expected type-checking violation exception when passed an
    # invalid parameter violating the type hint annotating that parameter.
    with raises(BeartypeCallHintParamViolation):
        equinox_module.munge_array('A string is not a boolean.')
