#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **Decidedly Object-Oriented Runtime-checking (DOOR) multiprocessing
data** submodule.

This submodule forks Python subprocesses with the standard
:mod:`multiprocessing` package, each of which calls public statement-level
runtime type-checkers defined by the :mod:`beartype.door` subpackage. This logic
leverages the `__main__` dunder global accessible *only* from Python scripts and
*must* thus be isolated to this distinct submodule.
'''

# ....................{ IMPORTS                            }....................
from beartype.door import die_if_unbearable
from beartype.roar import BeartypeDoorHintViolation
from multiprocessing import Pool
from pytest import raises

# ....................{ CALLABLES                          }....................
def and_faster_still(beyond_all_human_speed: str) -> None:
    '''
    Arbitrary function calling the :func:`.die_if_unbearable` raiser.

    To enable the parent Python process to validate that this callable actually
    *was* successfully called, this callable prints the passed parameter as is
    to standard output.

    Note that the :meth:`.Pool.imap` method requires that the first parameter
    passed to that method be a callback. This is that callback.

    Parameters
    ----------
    beyond_all_human_speed : str
        Arbitrary string previously passed as the second parameter to the
        :meth:`.Pool.imap` method called below.
    '''

    # Type-check this string with this raiser.
    die_if_unbearable(beyond_all_human_speed, str)

    # Print this string.
    print(beyond_all_human_speed)

# ....................{ MAIN                               }....................
## If the unqualified basename of this submodule is that of the pseudo-module
# "__main__", then this submodule was actually run as a script via Python's
# standard command-line option "-m". In this case, this is the parent Python
# process forking child Python subprocess (rather than one of those child Python
# subprocesses).
if __name__ == '__main__':
    # Call the above function with a valid parameter, which then prints that
    # parameter to standard output.
    and_faster_still('And faster still, beyond all human speed,')

    # Assert that calling the above function with an invalid parameter from
    # within a forked Python subprocess raises the expected violation.
    with raises(BeartypeDoorHintViolation):
        # With a single-process multiprocessing pool...
        with Pool(processes=1) as pool:
            # Fork a single Python process calling the function defined above.
            tuple(pool.imap(and_faster_still, [42]))
