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
from beartype._cave._cavefast import (
    DictKeysViewType,
    DictValuesViewType,
)
from beartype._data.hint.datahinttyping import (
    DictTypeToAny,
    FrozenSetInts,
)
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.kind.map.utilmapset import merge_mappings_two
from collections import (
    ChainMap as ChainMapType,
    deque,
)

# ....................{ INFERERS                           }....................
def infer_hint_collection_builtin(
    obj: object, __beartype_obj_ids_seen__: FrozenSetInts) -> Optional[object]:
    '''
    **Builtin collection type hint** (i.e., subscripted C-based type whose
    instances contain one or more reiterable items) recursively validating the
    passed object (including *all* items transitively reachable from this
    object) if this object is an instance of a builtin collection type *or*
    :data:`None` otherwise (i.e., if this object is *not* an instance of a
    builtin collection type).

    This function *cannot* be memoized, due to necessarily accepting the
    ``__beartype_obj_ids_seen__`` parameter unique to each call to the parent
    :func:`beartype.door.infer_hint` function.

    Caveats
    -------
    This function exhibits:

    * **Average-case constant time complexity** :math:`O(1)`, which occurs when
      either:

      * The passed object is *not* a builtin collection.
      * The passed object is a builtin collection *and* the type of the passed
        object is a builtin collection type (e.g., :class:`list`).

    * **Worst-case linear time complexity** :math:`O(n)` where :math:`n` is the
      number of builtin collection types (e.g., :class:`list`, :class:`tuple`),
      which occurs when the passed object is a builtin collection *and* the type
      of the passed object actually subclasses a builtin collection type (e.g.,
      ``class MuhList(list): ...``).

    Parameters
    ----------
    obj : object
        Object to infer a type hint from.
    __beartype_obj_ids_seen__ : FrozenSet[int]
        **Recursion guard.** See also the parameter of the same name accepted by
        the :func:`beartype.door._func.infer.inferhint.infer_hint` function.

    Returns
    -------
    Optional[object]
        Either:

        * If this object is a builtin collection type, this type subscripted by
          the union of the child type hints validating *all* items of this
          collection (e.g., ``list[str]``).
        * Else, :data:`None`.
    '''

    # Hint to be returned, defaulting to "None" as a fallback.
    hint: object = None

    # Type of this object.
    obj_type = obj.__class__
    print(f'Inferring possibly builtin collection type {repr(obj_type)}...')

    # Builtin collection superclass of this type if this type is a subclass of a
    # builtin collection type *OR* "None" otherwise.
    hint_factory = _infer_hint_factory_collection_builtin(obj_type)

    # If this type is a subclass of a builtin collection type...
    if hint_factory:
        # print(f'Inferring iterable {repr(obj_type_collections_abc)} subscription...')

        # Avoid circular import dependencies.
        from beartype.door._func.infer._inferiterable import (
            infer_hint_iterable)

        # Hint recursively validating this collection (including *ALL* items
        # transitively reachable from this collection), defined by subscripting
        # this collection type by the union of the child type hints validating
        # all items recursively reachable from this collection.
        hint = infer_hint_iterable(
            iterable=obj,  # type: ignore[arg-type]
            hint_factory=hint_factory,
            __beartype_obj_ids_seen__=__beartype_obj_ids_seen__,
        )
    # Else, this type is *NOT* a subclass of a builtin collection type. In this
    # case, fallback to returning "None".

    # Return this hint.
    return hint

# ....................{ PRIVATE ~ inferers                 }....................
@callable_cached
def _infer_hint_factory_collection_builtin(cls: type) -> Optional[object]:
    '''
    **Builtin collection superclass** (i.e., unsubscripted C-based type whose
    instances contain one or more reiterable items) of the passed class if this
    class subclasses a builtin collection type *or* :data:`None` otherwise
    (i.e., if this class does *not* subclass a builtin collection type).

    This function does *not* return a type hint annotating the passed class.
    This function merely returns a subscriptable type hint factory suitable for
    the caller to subscript with a child type hint, which then produces the
    desired type hint annotating the passed class. Why this indirection? In a
    word: efficiency. If this function recursively inferred and returned a full
    type hint, this function would need to guard against infinite recursion by
    accepting the ``__beartype_obj_ids_seen__`` parameter also accepted by the
    parent :func:`beartype.door._func.infer.inferhint.infer_hint` function;
    doing so would prevent memoization, substantially reducing efficiency.

    This function is memoized for efficiency.

    Parameters
    ----------
    cls : type
        Class to be introspected.

    Returns
    -------
    Optional[object]
        Either:

        * If this class subclasses a builtin collection type, that type.
        * Else, :data:`None`.
    '''
    assert isinstance(cls, type), f'{repr(cls)} not type.'

    # ....................{ IS                             }....................
    # Hint factory describing this class if this class is a builtin collection
    # type (e.g., "list", "tuple") *OR* "None" otherwise.
    hint_factory: object = _COLLECTION_BUILTIN_TYPE_TO_HINT_FACTORY_get(cls)

    # If this class is a builtin collection type, return this hint factory.
    if hint_factory:
        # print(f'Inferred builtin collection {repr(cls)} factory {repr(hint_factory)}...')
        return hint_factory
    # Else, this class is *NOT* a builtin collection type. However, this class
    # could still be a proper subclass of a builtin collection type: e.g.,
    #     class MuhList(list): ...
    #
    # Further logic is required to detect which collection type this class
    # subclasses if any.

    # ....................{ SUBCLASS                       }....................
    # Set of all superclasses of the passed class (including the passed class,
    # which is of course its own superclass *AND* subclass, because set theory
    # just goes hard like that).
    #
    # Note that this includes the irrelevant root "object" superclass, which is
    # *NOT* a builtin collection type and is thus guaranteed to *NEVER* be
    # matched below. Although that superclass *COULD* be trivially sliced off
    # (e.g., with an assignment resembling "classes = set(cls.__mro__[:-1])"),
    # doing so only uselessly consumes more time than it saves. So it goes.
    classes = set(cls.__mro__)

    # If the intersection of the set of all superclasses of this class with the
    # set of all builtin collection types is the empty set, then this class does
    # *NOT* subclass a builtin collection type. In this case, silently reduce to
    # a noop.
    if not (classes & _COLLECTION_BUILTIN_TYPES):
        return None
    # Else, this intersection is non-empty. In this case, this class subclasses
    # a builtin collection type. Deciding which type that is, however, requires
    # a linear search through the set of all builtin collection types. So it is.

    # ....................{ SEARCH                         }....................
    # For each builtin collection type (e.g., "list") and the corresponding hint
    # factory describing that type (e.g., "typing.List")...
    for superclass, hint_factory in (
        _COLLECTION_BUILTIN_TYPE_TO_HINT_FACTORY_ITEMS):
        # If this superclass is in this set of all superclasses of this
        # class, then this class subclasses this superclass. In this case,
        # halt searching and return this superclass.
        if superclass in classes:
            break
        # Else, this superclass is *NOT* in this set of all superclasses of
        # this class. In this case, this class does *NOT* subclass this
        # superclass. In this case, continue searching.

    # Assert that the above search found this superclass. Note that this should
    # *ALWAYS* be true. Nonetheless, chaos is guaranteed. Thus we assert.
    assert hint_factory, (
        f'Builtin collection subclass {repr(cls)} '
        f'type hint factory not found.'
    )

    # Return this hint factory.
    return hint_factory

# ....................{ PRIVATE ~ mappings                 }....................
#FIXME: Probably overkill. This and the following dictionary should probably
#just be manually defined within "_COLLECTION_BUILTIN_TYPE_TO_HINT_FACTORY".

# Note that key-value pairs are intentionally defined in decreasing order of
# real-world commonality to reduce time costs in the average case.
_COLLECTION_BUILTIN_TYPE_TO_HINT_FACTORY_ARGS_1: DictTypeToAny = {
    tuple: Tuple,
    list: List,
    frozenset: FrozenSet,
    set: Set,
    deque: Deque,
    DictKeysViewType: KeysView,
    DictValuesViewType: ValuesView,
}
'''
Dictionary mapping from each **single-argument builtin collection type** (i.e.,
C-based type satisfying the :class:`collections.abc.Collection` protocol whose
corresponding type hint factory is subscriptable by only a single child type
hint) to that factory.
'''


#FIXME: Also add:
#* "Counter". Trivial, but annoying due to "Counter" being subscriptable *ONLY*
#  by keys rather than both keys and values. *sigh*
#* "ItemsView". Actually, "ItemsView" support will probably have to be
#  implemented manually. "ItemsViews" are really just iterables over 2-tuples.

# Note that key-value pairs are intentionally defined in decreasing order of
# real-world commonality to reduce time costs in the average case.
_COLLECTION_BUILTIN_TYPE_TO_HINT_FACTORY_MAPPING_ARGS_2: DictTypeToAny = {
    dict: Dict,
    ChainMapType: ChainMap,
}
'''
Dictionary mapping from each **dual-argument builtin mapping type** (i.e.,
C-based type satisfying the :class:`collections.abc.Mapping` protocol whose
corresponding type hint factory is subscriptable by both a key and value child
type hint) to that factory.
'''

# ....................{ PRIVATE ~ mappings : merge         }....................
_COLLECTION_BUILTIN_TYPE_TO_HINT_FACTORY: DictTypeToAny = (
    merge_mappings_two(  # type: ignore[assignment]
        _COLLECTION_BUILTIN_TYPE_TO_HINT_FACTORY_ARGS_1,
        _COLLECTION_BUILTIN_TYPE_TO_HINT_FACTORY_MAPPING_ARGS_2,
    )
)
'''
Dictionary mapping from each **builtin collection type** (i.e., C-based type
satisfying the :class:`collections.abc.Collection` protocol described by a
corresponding type hint factory) to that factory.
'''


_COLLECTION_BUILTIN_TYPE_TO_HINT_FACTORY_get = (
    _COLLECTION_BUILTIN_TYPE_TO_HINT_FACTORY.get)
'''
:meth:`._COLLECTION_BUILTIN_TYPE_TO_HINT_FACTORY.get` method, globalized for
negligible efficiency gains.
'''


_COLLECTION_BUILTIN_TYPE_TO_HINT_FACTORY_ITEMS = (
    _COLLECTION_BUILTIN_TYPE_TO_HINT_FACTORY.items())
'''
Iterable of all builtin collection types (e.g., :class:`list`) and the type hint
factories describing those types (e.g., :obj:`typing.List`).
'''

# ....................{ PRIVATE ~ sets                     }....................
_COLLECTION_BUILTIN_TYPES = _COLLECTION_BUILTIN_TYPE_TO_HINT_FACTORY.keys()
'''
Set of all **builtin collection types** (i.e., C-based types satisfying the
:class:`collections.abc.Collection` protocol).
'''
