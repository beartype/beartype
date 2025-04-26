#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide SQLAlchemy integration tests.

This submodule functionally tests the :mod:`beartype` package against the
third-party SQLAlchemy package.
'''

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To raise human-readable test errors, avoid importing from
# package-specific submodules at module scope.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
from beartype_test._util.mark.pytskip import skip_unless_package

# ....................{ TESTS                              }....................
@skip_unless_package('sqlalchemy')
def test_sqlalchemy_asyncsession() -> None:
    '''
    Integration test validating that the :mod:`beartype` package raises *no*
    unexpected exceptions when type-checking instances of the third-party
    :class:`sqlalchemy.ext.asyncio.AsyncSession` generic, whose non-triviality
    once caused :mod:`beartype` to raise spurious type-checking violations.
    '''

    # ....................{ IMPORTS                        }....................
    # Defer test-specific imports.
    from beartype.door import die_if_unbearable
    from beartype.typing import Optional
    from sqlalchemy.ext.asyncio import AsyncSession

    # ....................{ ASSERTS                        }....................
    # Assert that @beartype at least superficially supports this non-trivial
    # generic by generating type-checking code *WITHOUT* raising spurious
    # exceptions. Ideally, this test would fully instantiate an asynchronous
    # SQLALchemy session and pass that as well. Pragmatically, doing so is
    # predictably non-trivial and altogether not worth the hassle. KISS it, yo!
    die_if_unbearable(None, Optional[AsyncSession])
