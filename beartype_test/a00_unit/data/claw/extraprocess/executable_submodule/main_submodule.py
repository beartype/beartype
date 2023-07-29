#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **executable submodule beartype import hook package initialization
submodule** (i.e., data module mimicking real-world usage of the
:func:`beartype.claw.beartype_this_package` import hook from a top-level
third-party package submodule ``{some_package}.__init__`).
'''

# ....................{ IMPORTS                            }....................
from beartype.roar import BeartypeCallHintParamViolation
from pytest import raises

# ....................{ CALLABLES                          }....................
def and_silence(too_enamoured_of_that_voice: float) -> None:
    '''
    Arbitrary callable annotated by trivial PEP-compliant type hints.
    '''

    pass

# ....................{ MAIN                               }....................
# If the unqualified basename of this submodule is that of the pseudo-module
# "__main__", then this submodule was actually run as a script via Python's
# standard command-line option "-m". In this case...
if __name__ == '__main__':
    # Assert that calling the above function raises the expected violation.
    with raises(BeartypeCallHintParamViolation):
        and_silence('Locks its mute music in her rugged cell.')
