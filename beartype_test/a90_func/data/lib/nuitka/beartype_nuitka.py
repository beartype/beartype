#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2023 Beartype authors.
# See "LICENSE" for further details.

'''
**Nuitka-specific functional test script** (i.e., script intended to be
compiled by the third-party :mod:`nuitka` compiler).

This script exercises the expected relationship between the
:mod:`beartype.beartype` decorator and the :mod:`nuitka` compiler by ensuring
:mod:`nuitka` successfully compiles scripts leveraging that decorator.
'''

# ....................{ IMPORTS                            }....................
from beartype import beartype
from beartype.door import TypeHint
from beartype.typing import Tuple, Union

# ....................{ FUNCTIONS                          }....................
@beartype
def make_type_hints() -> Tuple[TypeHint, ...]:
    '''
    Non-empty tuple containing one or more :class:`beartype.door.TypeHint`
    instances, exercising that :mod:`nuitka` supports those instances.
    '''

    hint = Union[int, float]
    type_hints = TypeHint(hint)
    return tuple(t for t in type_hints)

# ....................{ MAIN                               }....................
# Print the representations of these "TypeHint" instances for verifiability.
for type_hint in make_type_hints():
    print(type_hint)
