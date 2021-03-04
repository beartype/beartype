#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2021 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype `PEP 585`_**-compliant type hint data.**

This private submodule is *not* intended for importation by downstream callers.

.. _PEP 585:
    https://www.python.org/dev/peps/pep-0585
'''

# ....................{ IMPORTS                           }....................
from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_9
from beartype._util.utilobject import Iota
from typing import Any, FrozenSet

# See the "beartype.cave" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ HINTS                             }....................
HINT_PEP585_TUPLE_EMPTY = (
    tuple[()] if IS_PYTHON_AT_LEAST_3_9 else Iota())  # type: ignore[misc]
'''
`PEP 585`_-compliant empty fixed-length tuple type hint if the active Python
interpreter supports at least Python 3.9 and thus `PEP 585`_ *or* a unique
placeholder object otherwise to guarantee failure when comparing arbitrary
objects against this object via equality tests.

.. _PEP 585:
    https://www.python.org/dev/peps/pep-0585
'''

# ....................{ SETS ~ sign                       }....................
HINT_PEP585_SIGNS_SUPPORTED_DEEP: FrozenSet[Any] = frozenset()
'''
Frozen set of all `PEP 585`_-compliant **deeply supported signs** (i.e.,
arbitrary objects uniquely identifying `PEP 585`_-compliant type hints for
which the :func:`beartype.beartype` decorator generates deep type-checking
code).

.. _PEP 585:
    https://www.python.org/dev/peps/pep-0585
'''


HINT_PEP585_SIGNS_TYPE: FrozenSet[Any] = frozenset()
'''
Frozen set of all `PEP 585`_-compliant **standard class signs** (i.e.,
instances of the builtin :mod:`type` type uniquely identifying PEP-compliant
type hints).

.. _PEP 585:
    https://www.python.org/dev/peps/pep-0585
'''

# ....................{ SETS ~ sign : category            }....................
HINT_PEP585_SIGNS_SEQUENCE_STANDARD: FrozenSet[Any] = frozenset()
'''
Frozen set of all `PEP 585`_-compliant **standard sequence signs** (i.e.,
arbitrary objects uniquely identifying `PEP 585`_-compliant type hints
accepting exactly one subscripted type hint argument constraining *all* items
of compliant sequences, which necessarily satisfy the
:class:`collections.abc.Sequence` protocol with guaranteed ``O(1)`` indexation
across all sequence items).

.. _PEP 585:
    https://www.python.org/dev/peps/pep-0585
'''


HINT_PEP585_SIGNS_TUPLE: FrozenSet[Any] = frozenset()
'''
Frozen set of all `PEP 585`_-compliant **tuple signs** (i.e., arbitrary objects
uniquely identifying `PEP 585`_-compliant type hints accepting exactly one
subscripted type hint argument constraining *all* items of compliant tuples).

.. _PEP 585:
    https://www.python.org/dev/peps/pep-0585
'''

# ....................{ INITIALIZERS                      }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # ..................{ VERSIONS                          }..................
    # If the active Python interpreter does *NOT* target at least Python >= 3.9
    # and thus fails to support PEP 585, silently reduce to a noop.
    if not IS_PYTHON_AT_LEAST_3_9:
        return
    # Else, the active Python interpreter targets at least Python >= 3.9 and
    # thus supports PEP 585.

    # ..................{ IMPORTS                           }..................
    # Defer Python >= 3.9-specific imports.
    from collections import (
        deque,
        defaultdict,
        ChainMap,
        Counter,
        OrderedDict,
    )
    from collections.abc import (
        AsyncGenerator,
        AsyncIterable,
        AsyncIterator,
        Awaitable,
        ByteString,
        Callable,
        Collection,
        Container,
        Coroutine,
        Generator,
        ItemsView,
        Iterable,
        Iterator,
        KeysView,
        MappingView,
        Mapping,
        MutableMapping,
        MutableSequence,
        MutableSet,
        Reversible,
        Sequence,
        Set,
        ValuesView,
    )
    from contextlib import (
        AbstractAsyncContextManager,
        AbstractContextManager,
    )
    from re import (
        Match,
        Pattern,
    )

    # ..................{ GLOBALS                           }..................
    # Submodule globals to be redefined below.
    global \
        HINT_PEP585_SIGNS_SEQUENCE_STANDARD, \
        HINT_PEP585_SIGNS_SUPPORTED_DEEP, \
        HINT_PEP585_SIGNS_TUPLE, \
        HINT_PEP585_SIGNS_TYPE

    # ..................{ SETS ~ sign                       }..................
    HINT_PEP585_SIGNS_SUPPORTED_DEEP = frozenset((
        list,
        tuple,
        ByteString,
        MutableSequence,
        Sequence,
    ))
    HINT_PEP585_SIGNS_TYPE = frozenset((
        defaultdict,
        deque,
        dict,
        frozenset,
        list,
        set,
        tuple,
        type,
        AbstractAsyncContextManager,
        AbstractContextManager,
        AsyncGenerator,
        AsyncIterable,
        AsyncIterator,
        Awaitable,
        ByteString,
        Callable,
        ChainMap,
        Collection,
        Container,
        Coroutine,
        Counter,
        Generator,
        ItemsView,
        Iterable,
        Iterator,
        KeysView,
        MappingView,
        Mapping,
        Match,
        MutableMapping,
        MutableSequence,
        MutableSet,
        OrderedDict,
        Pattern,
        Reversible,
        Sequence,
        Set,
        ValuesView,
    ))

    # ..................{ SETS ~ sign : category            }..................
    HINT_PEP585_SIGNS_SEQUENCE_STANDARD = frozenset((
        list,
        ByteString,
        MutableSequence,
        Sequence,
    ))
    HINT_PEP585_SIGNS_TUPLE = frozenset((tuple,))


# Initialize this submodule.
_init()
