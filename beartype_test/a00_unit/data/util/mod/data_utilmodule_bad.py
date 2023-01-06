#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **unimportable data submodule.**

This submodule exercises dynamic importability by providing an unimportable
submodule defining an arbitrary attribute. External unit tests are expected to
dynamically import this attribute from this submodule.
'''

# ....................{ EXCEPTIONS                        }....................
raise ValueError(
    'Can you imagine a fulfilled society? '
    'Whoa, what would everyone do?'
)
