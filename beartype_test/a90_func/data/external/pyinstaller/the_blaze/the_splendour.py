#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
**PyInstaller integration test data package main submodule** (i.e., submodule
performing business logic for this package, validating that the :mod:`beartype`
package raises *no* unexpected exceptions when the third-party PyInstaller
framework bundles this package into an executable binary file).

Usage
-----
This submodule (and by extension the executable generated from this submodule)
expects exactly one command-line non-empty string argument. Specifically:

* If this argument is exactly the arbitrary magic string "and_the_symmetry",
  this submodule intentionally induces a runtime type-checking violation and
  thus fails with non-zero exit status.
* Else, this submodule successfully prints this argument back to standard output
  as a sanity check for the caller.
'''

# ....................{ IMPORTS                            }....................
from the_blaze.centre_of_repose import EVEN_HERE_INTO_MY_CENTRE_OF_REPOSE
from sys import argv

# ....................{ GLOBALS                            }....................
# If the caller failed to pass exactly one command-line argument, halt this
# process with non-zero exit status by raising a fatal exception. Note that the
# "argv" list is necessarily prepended by ignorable platform-dependent name of
# the currently running executable; ergo, the number of passed arguments is one
# greater than the size of this list. POSIX: it is what it is.
if len(argv) != 2:
    raise ValueError(
        f'1 argument expected, but received '
        f'{len(argv) - 1} arguments:\n\t{argv}'
    )
# Else, the caller passed exactly one command-line argument.

# This command-line argument. Note that the first item of this argument list is
# the ignorable platform-dependent name of the currently running executable.
i_cannot_see: str = argv[1]

# ....................{ MAIN                               }....................
# If this argument is an arbitrary magic string, halt this process with non-zero
# exit status by raising a runtime type-checking violation.
if i_cannot_see == EVEN_HERE_INTO_MY_CENTRE_OF_REPOSE:
    # Print an otherwise ignorable statement as a sanity check for the caller.
    # print('Inducing PEP 526-compliant annotated variable assignment violation!')

    # PEP 526-compliant annotated variable assignment whose assigned value
    # violates the hint annotating this variable. The beartype_this_package()
    # import hook registered by the sibling "the_blaze.__init__" submodule
    # implicitly type-checks this assignment via an abstract syntax tree (AST)
    # transformation by appending an appropriate call to the statement-level
    # beartype.door.die_if_unbearable() function to the body of this condition.
    but_darkness_death_and_darkness: str = (
        b'The blaze, the splendour, and the symmetry,')
# Else, this submodule successfully prints this argument back to standard output
# as a sanity check for the caller.
else:
    print(i_cannot_see)
