#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **importable data submodule.**

This submodule exercises dynamic importability by providing an importable
submodule defining an arbitrary attribute. External unit tests are expected to
dynamically import this attribute from this submodule.
'''

# ....................{ ATTRIBUTES                        }....................
attrgood = (
    "I started to see human beings as little lonesome, water based, pink "
    "meat, life forms pushing air through themselves and making noises that "
    "the other little pieces of meat seemed to understand. I was thinking to "
    "myself, \"There's five billion people here but we've never been more "
    "isolated.\" The only result of the aggressive individualism we pursue is "
    "that you lose sight of your compassion and we go to bed at night "
    "thinking \"Is this all there is?\" because we don't feel fulfilled."
)
'''
Arbitrary module-scope attribute.
'''
