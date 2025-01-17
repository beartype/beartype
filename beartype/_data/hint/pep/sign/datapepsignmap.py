#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2025 Beartype authors.
# See "LICENSE" for further details.

'''
Project-wide **type hint sign mappings** (i.e., dictionary globals mapping from
instances of the :class:`beartype._data.hint.pep.sign.datapepsigncls.HintSign`
class to various metadata associated with categories of type hints).

This private submodule is *not* intended for importation by downstream callers.
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import Dict
from beartype._data.hint.pep.sign.datapepsigncls import HintSign
from beartype._data.hint.pep.sign.datapepsigns import (
    HintSignAbstractSet,
    HintSignAsyncContextManager,
    HintSignAsyncGenerator,
    HintSignAsyncIterator,
    HintSignAsyncIterable,
    HintSignAwaitable,
    # HintSignByteString,
    HintSignChainMap,
    HintSignCollection,
    HintSignContainer,
    HintSignContextManager,
    HintSignCoroutine,
    HintSignCounter,
    HintSignDefaultDict,
    HintSignDeque,
    HintSignDict,
    HintSignFrozenSet,
    HintSignGenerator,
    HintSignItemsView,
    HintSignIterable,
    HintSignIterator,
    HintSignKeysView,
    HintSignList,
    HintSignMapping,
    HintSignMappingView,
    HintSignMatch,
    HintSignMutableMapping,
    HintSignMutableSequence,
    HintSignMutableSet,
    HintSignOrderedDict,
    HintSignPattern,
    HintSignReversible,
    HintSignSequence,
    HintSignSet,
    HintSignTuple,
    HintSignType,
    HintSignValuesView,
)

# ....................{ PRIVATE ~ globals                  }....................
# Note that the builtin "range" class:
# * Initializer "range.__init__(start, stop)" is effectively instantiated as
#   [start, stop) -- that is to say, such that:
#   * The initial "start" integer is *INCLUSIVE* (i.e., the instantiated range
#     includes this integer).
#   * The final "stop" integer is *EXCLUSIVE* (i.e., the instantiated range
#     excludes this integer).
# * Publicizes these integers as the instance variables "start" and "stop" such
#   that these invariants are guaranteed:
#       >>> range(min, max).start == min
#       True
#       >>> range(min, max).stop == max
#       True

_ARGS_LEN_0 = range(0, 1)  # == [0, 1) == [0, 0]
'''
**Zero-argument length range** (i.e., :class:`range` instance effectively
equivalent to the integer ``0``, describing type hint factories subscriptable by
*no* child type hints).
'''


_ARGS_LEN_1 = range(1, 2)  # == [1, 2) == [1, 1]
'''
**One-argument length range** (i.e., :class:`range` instance effectively
equivalent to the integer ``1``, describing type hint factories subscriptable by
exactly one child type hint).
'''


_ARGS_LEN_2 = range(2, 3)  # == [2, 3) == [2, 2]
'''
**Two-argument length range** (i.e., :class:`range` instance effectively
equivalent to the integer ``2``, describing type hint factories subscriptable by
exactly two child type hints).
'''


_ARGS_LEN_3 = range(3, 4)  # == [3, 4) == [3, 3]
'''
**Three-argument length range** (i.e., :class:`range` instance effectively
equivalent to the integer ``3``, describing type hint factories subscriptable by
exactly three child type hints).
'''


_ARGS_LEN_1_OR_2 = range(1, 3)  # == [1, 3) == [1, 2]
'''
**One- or two-argument length range** (i.e., :class:`range` instance effectively
equivalent to the integer range ``[1, 2]``, describing type hint factories
subscriptable by either one or two child type hints).
'''

# ....................{ SIGNS ~ origin : args              }....................
# Fully initialized by the _init() function below.
HINT_SIGN_ORIGIN_ISINSTANCEABLE_TO_ARGS_LEN_RANGE: Dict[HintSign, range] = {
    # Type hint factories subscriptable by exactly one child type hint.
    HintSignAbstractSet: _ARGS_LEN_1,
    HintSignAsyncIterable: _ARGS_LEN_1,
    HintSignAsyncIterator: _ARGS_LEN_1,
    HintSignAwaitable: _ARGS_LEN_1,
    # HintSignByteString: _ARGS_LEN_1,
    HintSignCollection: _ARGS_LEN_1,
    HintSignContainer: _ARGS_LEN_1,
    HintSignCounter: _ARGS_LEN_1,
    HintSignDeque: _ARGS_LEN_1,
    HintSignFrozenSet: _ARGS_LEN_1,
    HintSignIterable: _ARGS_LEN_1,
    HintSignIterator: _ARGS_LEN_1,
    HintSignKeysView: _ARGS_LEN_1,
    HintSignList: _ARGS_LEN_1,
    HintSignMatch: _ARGS_LEN_1,
    HintSignMappingView: _ARGS_LEN_1,
    HintSignMutableSequence: _ARGS_LEN_1,
    HintSignMutableSet: _ARGS_LEN_1,
    HintSignPattern: _ARGS_LEN_1,
    HintSignReversible: _ARGS_LEN_1,
    HintSignSequence: _ARGS_LEN_1,
    HintSignSet: _ARGS_LEN_1,
    HintSignType: _ARGS_LEN_1,
    HintSignValuesView: _ARGS_LEN_1,

    # Type hint factories subscriptable by exactly two child type hints.
    HintSignAsyncGenerator: _ARGS_LEN_2,
    HintSignChainMap: _ARGS_LEN_2,
    HintSignDefaultDict: _ARGS_LEN_2,
    HintSignDict: _ARGS_LEN_2,
    HintSignItemsView: _ARGS_LEN_2,
    HintSignMapping: _ARGS_LEN_2,
    HintSignMutableMapping: _ARGS_LEN_2,
    HintSignOrderedDict: _ARGS_LEN_2,
    HintSignTuple: _ARGS_LEN_2,

    # Type hint factories subscriptable by exactly three child type hints.
    HintSignCoroutine: _ARGS_LEN_3,
    HintSignGenerator: _ARGS_LEN_3,
}
'''
Dictionary mapping from each sign uniquely identifying a PEP-compliant type hint
factory originating from an **isinstanceable origin type** (i.e., isinstanceable
class such that *all* objects satisfying type hints created by subscripting this
factory are instances of this class) to this factory's **argument length range**
(i.e., :class:`range` instance describing the minimum and maximum number of
child type hints that may subscript this factory).
'''

# ....................{ PRIVATE ~ main                     }....................
def _init() -> None:
    '''
    Initialize this submodule.
    '''

    # Defer function-specific imports.
    from beartype._util.py.utilpyversion import IS_PYTHON_AT_LEAST_3_13

    # If the active Python interpreter targets Python >= 3.13...
    if IS_PYTHON_AT_LEAST_3_13:
        # Add all signs uniquely identifying one- or two-argument type hint
        # factories under Python >= 3.13, which generalized various one-argument
        # type hint factories to accept an additional optional child type hint
        # via "PEP 696 – Type Defaults for Type Parameters".
        HINT_SIGN_ORIGIN_ISINSTANCEABLE_TO_ARGS_LEN_RANGE.update({
            HintSignAsyncContextManager: _ARGS_LEN_1_OR_2,
            HintSignContextManager: _ARGS_LEN_1_OR_2,
        })
    # Else, the active Python interpreter targets Python <= 3.12. In this
    # case...
    else:
        # Add all signs uniquely identifying two-argument type hint factories
        # under Python <= 3.12.
        HINT_SIGN_ORIGIN_ISINSTANCEABLE_TO_ARGS_LEN_RANGE.update({
            HintSignAsyncContextManager: _ARGS_LEN_1,
            HintSignContextManager: _ARGS_LEN_1,
        })
    # print(f'HINT_SIGN_ORIGIN_ISINSTANCEABLE_TO_ARGS_LEN_RANGE: {HINT_SIGN_ORIGIN_ISINSTANCEABLE_TO_ARGS_LEN_RANGE}')


# Initialize this submodule.
_init()
