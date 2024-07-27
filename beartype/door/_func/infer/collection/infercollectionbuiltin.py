#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) procedural
builtin collections type hint inferrers** (i.e., high-level functions
dynamically subscripted type hints that best describe instances of builtin
C-based container types).
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    Dict,
    ChainMap,
    Deque,
    FrozenSet,
    KeysView,
    List,
    Optional,
    Set,
    Tuple,
    ValuesView,
)
from beartype._data.hint.datahinttyping import (
    DictStrToAny,
    DictTypeToAny,
    FrozenSetInts,
    FrozenSetStrs,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.kind.map.utilmapset import merge_mappings_two
from beartype._util.utilobjectattr import (
    get_object_methods_name_to_value_explicit)
from collections import (
    ChainMap as ChainMapType,
    deque,
)
from collections.abc import (
    Iterable as IterableABC,
    KeysView as KeysViewABC,
    ValuesView as ValuesViewABC,
)

# ....................{ TYPES ~ hint                       }....................
# Note that key-value pairs are intentionally defined in decreasing order of
# real-world commonality to reduce time costs in the average case.
_TYPE_TO_HINT_FACTORY_COLLECTION_ARGS_1: DictTypeToAny = {
    tuple: Tuple,
    list: List,
    frozenset: FrozenSet,
    set: Set,
    deque: Deque,
    KeysViewABC: KeysView,
    ValuesViewABC: ValuesView,
}
'''
Dictionary mapping from each **concrete single-argument collection type** (i.e.,
standard non-abstract Python types satisfying the
:class:`collections.abc.Collection` protocol whose corresponding type hint
factories are subscriptable by only a single child type hint) to those
factories.
'''


#FIXME: Also add:
#* "Counter". Trivial, but annoying due to "Counter" being subscriptable *ONLY*
#  by keys rather than both keys and values. *sigh*
#* "ItemsView". Actually, "ItemsView" support will probably have to be
#  implemented manually. "ItemsViews" are really just iterables over 2-tuples.
# Note that key-value pairs are intentionally defined in decreasing order of
# real-world commonality to reduce time costs in the average case.
_TYPE_TO_HINT_FACTORY_MAPPING_ARGS_2: DictTypeToAny = {
    dict: Dict,
    ChainMapType: ChainMap,
}
'''
Dictionary mapping from each **concrete dual-argument mapping type** (i.e.,
standard non-abstract Python types satisfying the
:class:`collections.abc.Mapping` protocol whose corresponding type hint
factories are subscriptable by both a key and value child type hint) to those
factories.
'''


#FIXME: Docstring us up, please.
_TYPE_TO_HINT_FACTORY_ITERABLE: DictTypeToAny = merge_mappings_two(  # type: ignore[assignment]
    _TYPE_TO_HINT_FACTORY_COLLECTION_ARGS_1,
    _TYPE_TO_HINT_FACTORY_MAPPING_ARGS_2,
)
