#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright (c) 2014-2020 Cecil Curry.
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

# See the "beartype.__init__" submodule for further commentary.
__all__ = ['STAR_IMPORTS_CONSIDERED_HARMFUL']

# ....................{ HINTS                             }....................
HINT_PEP585_TUPLE_EMPTY = tuple[()] if IS_PYTHON_AT_LEAST_3_9 else Iota()
'''
`PEP 585`_-compliant empty fixed-length tuple type hint if the active Python
interpreter supports at least Python 3.9 and thus `PEP 585`_ *or* a unique
placeholder object otherwise to guarantee failure when comparing arbitrary
objects against this object via equality tests.

.. _PEP 585:
    https://www.python.org/dev/peps/pep-0585
'''

# ....................{ ADDERS                            }....................
def add_data(data_module: 'ModuleType') -> None:
    '''
    Add `PEP 585`_**-compliant type hint data to various global containers
    declared by the passed module.

    Parameters
    ----------
    data_module : ModuleType
        Module to be added to.

    .. _PEP 585:
        https://www.python.org/dev/peps/pep-0585
    '''

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

    # ..................{ SETS ~ signs : type               }..................
    # Tuple of all PEP 585-compliant standard class signs (i.e., instances of
    # the builtin "type" type identifying PEP 585-compliant type hints).
    _HINT_PEP585_SIGNS_TYPE = (
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
    )

    data_module.HINT_PEP_SIGNS_TYPE.update(_HINT_PEP585_SIGNS_TYPE)
    data_module.HINT_PEP_SIGNS_TYPE_ORIGIN.update(_HINT_PEP585_SIGNS_TYPE)

    # ..................{ SETS ~ signs : supported          }..................
    data_module.HINT_PEP_SIGNS_SUPPORTED_DEEP.update((
        list,
        tuple,
        ByteString,
        MutableSequence,
        Sequence,
    ))

    # ..................{ SETS ~ signs : subtypes           }..................
    data_module.HINT_PEP_SIGNS_SEQUENCE_STANDARD.update((
        list,
        ByteString,
        MutableSequence,
        Sequence,
    ))
    data_module.HINT_PEP_SIGNS_TUPLE.update((
        tuple,
    ))
