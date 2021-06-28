#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype :pep:`484`**-compliant type hint data.**

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                           }....................
import typing
from beartype._util.data.hint.pep.datapepmodule import HINT_PEP_MODULE_NAMES
from beartype._util.py.utilpyversion import (
    IS_PYTHON_AT_LEAST_3_9,
    IS_PYTHON_AT_LEAST_3_7,
)
from typing import Tuple

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ BASES                             }....................
# Conditionally add the "typing.ForwardRef" superclass depending on the
# current Python version, as this superclass was thankfully publicized
# under Python >= 3.7 after its initial privatization under Python <= 3.6.
HINT_PEP484_TYPE_FORWARDREF = (
    typing.ForwardRef if IS_PYTHON_AT_LEAST_3_7 else
    typing._ForwardRef  # type: ignore [attr-defined]
)
'''
**Forward reference sign** (i.e., arbitrary objects uniquely identifying a
:pep:`484`-compliant type hint unifying one or more subscripted type hint
arguments into a disjunctive set union of these arguments).
'''

# ....................{ HINTS                             }....................
HINT_PEP484_TUPLE_EMPTY = Tuple[()]
'''
:pep:`484`-compliant empty fixed-length tuple type hint.
'''

# ....................{ SETS                              }....................
HINT_PEP484_BARE_REPRS_DEPRECATED = frozenset(
    # If the active Python interpreter targets Python >= 3.9 and thus
    # supports PEP 585, list all bare PEP 484-compliant representations (e.g.,
    # "typing.List") that have since been obsoleted by equivalent bare PEP
    # 585-compliant representations (e.g., "list"), defined as...
    (
        # Each representation relative to each module name...
        f'{typing_module_name}.{hint_bare_repr}'
        # For each bare deprecated PEP 484-compliant representation...
        for hint_bare_repr in {
            'AbstractSet',
            'AbstractSet',
            'AsyncContextManager',
            'AsyncGenerator',
            'AsyncIterable',
            'AsyncIterator',
            'Awaitable',
            'ByteString',
            'Callable',
            'ChainMap',
            'Collection',
            'Container',
            'ContextManager',
            'Coroutine',
            'Counter',
            'DefaultDict',
            'Deque',
            'Dict',
            'FrozenSet',
            'Generator',
            'Hashable',
            'ItemsView',
            'Iterable',
            'Iterator',
            'KeysView',
            'List',
            'MappingView',
            'Mapping',
            'Match',
            'MutableMapping',
            'MutableSequence',
            'MutableSet',
            'OrderedDict',
            'Pattern',
            'Reversible',
            'Sequence',
            'Set',
            'Sized',
            'Tuple',
            'Type',
            'ValuesView',
        }
        # For the name of each top-level hinting module...
        for typing_module_name in HINT_PEP_MODULE_NAMES
    ) if IS_PYTHON_AT_LEAST_3_9 else
    # Else, the active Python interpreter only targets Python < 3.9 and thus
    # fails to support PEP 585. In this case, deprecate nothing.
    ()
)
'''
Frozen set of all :pep:`484`-compliant **deprecated typing attributes** (i.e.,
:pep:`484`-compliant :mod:`typing` type hints obsoleted by more recent PEPs).
'''
