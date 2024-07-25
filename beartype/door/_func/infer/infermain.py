#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) procedural
type hint inferrers** (i.e., high-level functions dynamically inferring the type
hints best describing arbitrary objects).
'''

# ....................{ TODO                               }....................
#FIXME: Consider defining a memoized "BeartypeInferHintConf" dataclass modelled
#after the memoized "BeartypeConf" dataclass, enabling callers to efficiently
#configure type hint inference.

# ....................{ IMPORTS                            }....................
from beartype.door._func.infer._infercontainer import infer_hint_container
from beartype.roar import BeartypeDoorInferHintRecursionWarning
from beartype.typing import (
    ChainMap,
    Deque,
    Dict,
    FrozenSet,
    KeysView,
    List,
    Set,
    Tuple,
    Type,
    ValuesView,
)
from beartype._data.hint.datahinttyping import DictStrToAny
from beartype._util.error.utilerrwarn import issue_warning
from beartype._util.utilobject import get_object_type_name

# ....................{ CLASSES                            }....................
class BeartypeInferHintContainerRecursion(object):
    '''
    Child type hint subscripting all **recursive container type hints** (i.e.,
    parent type hints describing a container containing one or more items
    self-referentially referring to the same container).
    '''

    def __repr__(self) -> str:
        return 'RecursiveContainer'

# ....................{ INFERERS                           }....................
#FIXME: Add support for dictionaries. That's pretty much mandatory. Pretty much
#useless without at least that. *sigh*
#FIXME: Special-case instances of all other builtin types (e.g., integers,
#strings) to immediately return those types for efficiency.
def infer_hint(
    # Mandatory parameters.
    obj: object,

    # Hidden parameters. *GULP*
    __beartype_obj_ids_seen__: FrozenSet[int] = frozenset(),
) -> object:
    '''
    Type hint annotating the passed object.

    This function dynamically infers (i.e., computes, decides, deduces) a type
    hint sufficient for annotating (i.e., describing, matching, validating) the
    passed object.

    Caveats
    -------
    **This function explicitly guards against infinite recursion.** Notably,
    this function accepts **recursive containers** (i.e., pure-Python containers
    containing one or more items whose values self-referentially refer to the
    same containers). When passed a recursive container, this function guards
    against infinite recursion that would otherwise be induced by that container
    by instead returning a placeholder instance of the
    :class:`.BeartypeInferHintRecursion` class describing this recursion: e.g.,

    .. code-block:: python

       # Define a trivial recursive list.
       >>> recursive_list = ['this is fine', b'this is fine too, but...',]
       >>> recursive_list.append(recursive_list)

       # Infer the type hint annotating this list.
       >>> from beartype.door import infer_hint
       >>> infer_hint(recursive_list)
       ##FIXME: INSERT SANE REPR HERE, PLEASE. *sigh*

    **This function exhibits best-, average-, and worst-case** :math:`O(n)`
    **linear-time complexity** for :math:`n` the number of nested items
    transitively contained in the passed object if this object is a container.
    This differs from most of the public :mod:`beartype` API, which exhibits at
    worst worst-case amortized :math:`O(1)` constant-time complexity. Although
    this function could certainly be generalized to support that sort of
    constant-time complexity, doing so would be largely pointless. Type hint
    inference only has real-world value insofar as it accurately infers hints.
    Inference operating in :math:`O(1)` time would necessarily be inaccurate and
    thus of *no* real-world value. Inference operating in :math:`O(n)` time, on
    the other hand, accurately infers hints for even arbitrarily large
    pure-Python containers by introspecting all objects transitively reachable
    from those containers.

    **This function cannot be reasonably memoized** (e.g., via the
    :func:`beartype._util.cache.utilcachecall.callable_cached` decorator).
    Technically, this function *could* be memoized... *sorta.* Pragmatically,
    this function *cannot* be memoized. Most arbitrary objects are mutable and
    thus unhashable and thus unmemoizable. While feasible, memoizing this
    function for the small subset of arbitrary objects that are immutable would
    dramatically increase the space complexity of this function. In short,
    memoizing arbitrary objects is effectively infeasible.

    Parameters
    ----------
    obj : object
        Arbitrary object to infer a type hint from.
    __beartype_obj_ids_seen__ : FrozenSet[int]
        **Recursion guard** (i.e., frozen set of the integers uniquely
        identifying all previously visited containers passed as the ``obj``
        parameter to some recursive parent call of this same function on the
        current call stack). If the object identifier (ID) of passed object
        already resides in this recursion guard, then that object has already
        been visited by a prior call to this function in the same call stack
        and is thus a recursive container; in that case, this function
        short-circuits infinite recursion by returning a placeholder instance of
        the :class:`.BeartypeInferHintRecursion` class describing this issue.

    Returns
    -------
    object
        Type hint inferred from the passed object.

    Warns
    -----
    BeartypeDoorInferHintRecursionWarning
        On detecting that the passed object is **recursive** (i.e.,
        self-referentially refers to itself, typically due to being a container
        containing one or more items that self-referentially refer to that same
        container).
    '''

    # ....................{ PROTECTION                     }....................
    # If the integer uniquely identifying this object already resides in this
    # recursion guard, this object has already been visited by a prior call to
    # this function in the same call stack and is thus a recursive container.
    # In this case...
    if id(obj) in __beartype_obj_ids_seen__:
        # Emit a non-fatal warning informing the caller.
        issue_warning(
            cls=BeartypeDoorInferHintRecursionWarning,
            message=(
                f'Container recursion detected; short-circuiting for safety. '
                f'Container {type(obj)} self-referentially refers to '
                f'same container.'
            ),
        )

        # Short-circuit infinite recursion by creating and returning a
        # placeholder instance of a dataclass describing this situation.
        return BeartypeInferHintContainerRecursion
    # Else, this object has yet to be visited.

    # ....................{ PEP 484                        }....................
    # If this object is the "None" singleton, this object is trivially satisfied
    # by itself under PEP 484. Interestingly, "None" is the *ONLY* object that
    # is its own type hint.
    elif obj is None:
        return obj
    # Else, this object is *NOT* the "None" singleton.

    # ....................{ PEP [484|585] ~ type           }....................
    # If this object is a type, this type is trivially satisfied by a PEP 484-
    # or 585-compliant subclass type hint subscripted by this type.
    elif isinstance(obj, type):
        return Type[obj]
    # Else, this object is *NOT* a type.

    # ....................{ NON-PEP ~ scalar               }....................
    # Type of this object.
    obj_type = obj.__class__

    # If this object is a builtin scalar (e.g., integer, string), return this
    # type as is.
    #
    # Note that this is *NOT* simply a negligible optimization, although it
    # certainly is that as well. This is an essential sanity check to ensure
    # that strings are annotated as the builtin "str" type rather than the
    # recursive "collections.abc.Sequence[str]" type hint, which they otherwise
    # would be. Since strings are infinitely recursively immutable sequences of
    # immutable sequences, this detection avoids *INSANE* infinite recursion.
    if obj_type in _BUILTIN_SCALAR_TYPES:
        return obj_type
    # Else, this object is *NOT* a builtin scalar.

    # ....................{ PEP [484|585] ~ container      }....................
    #FIXME: [SPEED] Danger: string interpolation! This is probably shockingly
    #inefficient. Contemplate alternatives. Like, literally *ANYTHING* else.
    # Fully-qualified (i.e., absolute) name of the type of this object.
    obj_classname = get_object_type_name(obj)

    #FIXME: [SPEED] Negligible optimization here:
    #* Define a new global:
    #      _COLLECTION_CLASSNAME_TO_HINT_FACTORY_ARGS_1_get = (
    #          _COLLECTION_CLASSNAME_TO_HINT_FACTORY_ARGS_1.get)
    #* Call that global here.
    # Single-argument collection type hint factory that generates type hints
    # validating this object if this object is such a collection *OR* "None"
    # otherwise (i.e., if this object is *NOT* such a collection).
    hint_factory_args_1 = _COLLECTION_CLASSNAME_TO_HINT_FACTORY_ARGS_1.get(
        obj_classname)

    # If this object is validated by a single-argument collection type hint
    # factory, this object is a collection of zero or more items. In this
    # case...
    if hint_factory_args_1 is not None:
        # Parent type hint recursively validating this collection (including
        # *ALL* items transitively reachable from this collection), defined by
        # subscripting this factory by the union of the child type hints
        # validating all items recursively reachable from this collection.
        hint = infer_hint_container(
            container=obj,  # type: ignore[arg-type]
            hint_factory=hint_factory_args_1,
            __beartype_obj_ids_seen__=__beartype_obj_ids_seen__,
        )

        # Return this hint.
        return hint
    # Else, this object is *NOT* validated by such a factory.

    # ....................{ NON-PEP ~ collections.abc      }....................
    # Defer heavyweight imports. Notably:
    # * The "_infercollabc" submodule defines a deeply nested data structure
    #   literally implementing a full-blown *FRIGGIN' FINITE STATE MACHINE.* So,
    #   you just know that's heavy. It's heaviness is unmeasurable.
    from beartype.door._func.infer._infercollabc import (
        infer_hint_type_collections_abc)

    # Narrowest "collections.abc" protocol validating this type if at least one
    # such protocol validates this type *OR* "None" otherwise (i.e., if *NO*
    # such protocol validates this type).
    obj_type_collections_abc = infer_hint_type_collections_abc(obj_type)

    # If at least one "collections.abc" protocol validates this type...
    if obj_type_collections_abc:
        #FIXME: *INCORRECT.* Not all "collections.abc" protocols describe
        #containers, obviously. We sigh. We sigh so hard!
        # Parent type hint recursively validating this container (including
        # *ALL* items transitively reachable from this container), defined by
        # subscripting this "collections.abc" protocol by the union of the child
        # type hints validating all items recursively reachable from this
        # container.
        hint = infer_hint_container(
            container=obj,  # type: ignore[arg-type]
            hint_factory=obj_type_collections_abc,
            __beartype_obj_ids_seen__=__beartype_obj_ids_seen__,
        )

        # Return this hint.
        return hint
    # Else, *NO* "collections.abc" protocol validates this type.

    # ....................{ FALLBACK                       }....................
    # Return this type as a last-ditch fallback. By definition, *ANY* object is
    # trivially satisfied by a type hint that is the type of that object (e.g.,
    # the integer "42" is trivially satisfied by the builtin type "int").
    return obj_type

# ....................{ PRIVATE ~ mappings                 }....................
_COLLECTION_CLASSNAME_TO_HINT_FACTORY_ARGS_1: DictStrToAny = {
    'builtins.dict_keys': KeysView,
    'builtins.dict_values': ValuesView,
    'builtins.frozenset': FrozenSet,
    'builtins.list': List,
    'builtins.set': Set,
    'builtins.tuple': Tuple,
    'collections.deque': Deque,
}
'''
Dictionary mapping from the fully-qualified names of **single-argument
collection type hint factories** (i.e., standard Python types subscriptable by
only a single child type hint and satisfying the
:class:`collections.abc.Collection` protocol) to those factories.
'''


#FIXME: Also add:
#* "Counter". Trivial, but annoying due to "Counter" being subscriptable *ONLY*
#  by keys rather than both keys and values. *sigh*
#* "ItemsView". Actually, "ItemsView" support will probably have to be
#  implemented manually. "ItemsViews" are really just iterables over 2-tuples.
_MAPPING_CLASSNAME_TO_HINT_FACTORY_ARGS_2: DictStrToAny = {
    'builtins.dict': Dict,
    'collections.ChainMap': ChainMap,
}
'''
Dictionary mapping from the fully-qualified names of **dual-argument mapping
type hint factories** (i.e., standard Python types subscriptable by both key and
value child type hints and satisfying the :class:`collections.abc.Mapping`
protocol) to those factories.
'''

# ....................{ PRIVATE ~ sets                     }....................
#FIXME: Shift into the "beartype._data.cls" subpackage somewhere, please.
_BUILTIN_SCALAR_TYPES: FrozenSet[type] = frozenset((
    bytes,
    complex,
    float,
    int,
    str,
))
'''
Frozen set of all **builtin scalar types** (i.e., standard C-based types whose
instances are scalar values).
'''
