#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide Redis integration tests.

This submodule functionally tests the :mod:`beartype` package against the
third-party Redis package.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_unless_package

# ....................{ TESTS                              }....................
@skip_unless_package('redis')
def test_redis() -> None:
    '''
    Integration test validating that the :mod:`beartype` package raises *no*
    unexpected exceptions when decorating :pep:`557`-compliant dataclasses
    containing one or more fields annotated by the third-party
    :class:`redis.Redis` generic, whose extreme non-triviality once caused
    :mod:`beartype` to raise spurious decoration-time exceptions. Surprisingly,
    :class:`redis.Redis` transitively subclasses over 256 pseudo-superclasses!
    :class:`redis.Redis` is thus a real-world torture test for
    pseudo-superclass introspection and iteration.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype import beartype
    from dataclasses import dataclass
    from redis import Redis

    # ....................{ CLASSES                        }....................
    # Implicitly assert that the @beartype decorator successfully decorators a
    # PEP 557-compliant dataclass containing a Redis-annotated field. Although
    # instantiating this dataclass would also be useful, doing so is complicated
    # by the need to run a local Redis server of some sort. For the moment, the
    # trivial integration test suffices to avoid casual regressions.
    @beartype
    @dataclass
    class OnHeFlared(object):
        '''
        :pep:`557`-compliant dataclass decorated by :func:`.beartype`,
        containing one or more fields annotated by the third-party
        :class:`redis.Redis` generic.
        '''

        and_made_their: str
        '''
        Arbitrary field annotated by an arbitrary Redis-agnostic hint.
        '''

        dovewings_tremble: Redis
        '''
        Arbitrary field annotated by the :class:`redis.Redis` generic.
        '''
