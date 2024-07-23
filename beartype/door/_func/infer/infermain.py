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
from beartype._util.hint.pep.proposal.utilpep484604 import (
    make_hint_pep484604_union)
from beartype._util.utilobject import get_object_type_name
from enum import (
    Enum,
    auto as next_enum_member_value,
    unique as die_unless_enum_member_values_unique,
)

# ....................{ ENUMERATIONS                       }....................
#FIXME: Docstring us up, please.
#FIXME: Actually, this is non-ideal. Instead, we *probably* want to revert back
#to the class-based approach so that we can emit human-readable repr() strings
#resembling:
#    "Object recursion detected; short-circuiting for safety. Container {safe_repr(obj)} index {item_index}
#    item {safe_repr(item)} self-referentially refers to same container."
@die_unless_enum_member_values_unique
class BeartypeHintInferrence(Enum):
    '''
    Enumeration of all kinds of **type hint inferences** (i.e., ...).

    Attributes
    ----------
    RECURSIVE : EnumMemberType
        ...
    '''

    RECURSIVE = next_enum_member_value()


class BeartypeInferHintRecursion(object):
    '''

    '''

    def __repr__(self) -> str:
        return 'HintUnknown'

# ....................{ INFERERS                           }....................
#FIXME: Unit test us up, please.
#FIXME: Internally comment us up, please.
#FIXME: Add support for at least:
#* Dictionaries.
#* Literals.
#
#That's pretty much mandatory. Pretty much useless without at least that. *sigh*
#FIXME: Conditionally annotate tuples less than a certain fixed length (e.g., 10
#items) as fixed-length rather than variable-length tuple type hints. Yeah!
#FIXME: Conditionally represent unions as PEP 604-compliant "|"-delimited type
#unions for both conciseness and teachability. To do so, simply use the EAFP
#principle; efficiency is largely irrelevant here. Moreover, PEP 604 support
#widely varies across CPython versions -- with newer versions supporting more
#possible types for inclusion in PEP 604-compliant type unions. Don't even
#bother checking the current CPython version. Just EAFP all the way. Yeah!
#FIXME: Generalize to support user-defined subclasses of builtin container types
#(e.g., "list" subclasses). Note that doing so is complicated by Python 3.8,
#where those types are *NOT* subscriptable. Maybe ignore Python 3.8, honestly?
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
    '''

    # ....................{ RECURSION                      }....................
    # If the integer uniquely identifying this object already resides in this
    # recursion guard, this object has already been visited by a prior call to
    # this function in the same call stack and is thus a recursive container.
    # In this case, short-circuit infinite recursion by creating and returning a
    # placeholder instance of a dataclass describing this situation.
    if id(obj) in __beartype_obj_ids_seen__:
        return BeartypeHintInferrence.RECURSIVE
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

    # ....................{ PEP [484|585] ~ container      }....................
    # Fully-qualified (i.e., absolute) name of the type of this object.
    obj_classname = get_object_type_name(obj)

    # Single-argument collection type hint factory that generates type hints
    # validating this object if any *OR* "None" otherwise (i.e., if no such
    # factory validates this object).
    hint_factory_args_1 = _COLLECTION_CLASSNAME_TO_HINT_FACTORY_ARGS_1.get(
        obj_classname)

    # If this object is validated by a single-argument collection type hint
    # factory, this object is a collection of zero or more items. In this
    # case...
    if hint_factory_args_1 is not None:
        # Add the integer uniquely identifying this collection to this set to
        # note that this collection has now been visited by this recursion.
        __beartype_obj_ids_seen__ |= {id(obj)}

        # Set of all child type hints to conjoin into a union.
        hints_child = set()

        # For each item in this collection...
        for item in obj:  # type: ignore[attr-defined]
            # Child type hint validating this item.
            hint_child = infer_hint(
                obj=item,
                __beartype_obj_ids_seen__=__beartype_obj_ids_seen__,
            )

            # Add this child type hint to this set.
            hints_child.add(hint_child)

        # PEP 604- or 484-compliant union of these child type hints.
        hints_child_union = make_hint_pep484604_union(tuple(hints_child))

        # Parent type hint recursively validating this collection (including
        # *ALL* items transitively reachable from this collection), defined by
        # subscripting this factory by this union.
        hint = (
            hint_factory_args_1[hints_child_union, ...]  # type: ignore[index]
            if hint_factory_args_1 is Tuple else
            hint_factory_args_1[hints_child_union]  # type: ignore[index]
        )

        # Return this hint.
        return hint
    # Else, this object is *NOT* validated by such a factory.

    # ....................{ FALLBACK                       }....................
    # Type of this object.
    hint = type(obj)

    # Return this type as a last-ditch fallback. By definition, *ANY* object is
    # trivially satisfied by a type hint that is the type of that object (e.g.,
    # the integer "42" is trivially satisfied by the builtin type "int").
    return hint

# ....................{ PRIVATE ~ globals                  }....................
#FIXME: Shift into the "beartype._data.hint.pep" subpackage somewhere, please.
_COLLECTION_CLASSNAME_TO_HINT_FACTORY_ARGS_1: Dict[str, object] = {
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
#  be keys rather than both keys and values. *sigh*
_MAPPING_CLASSNAME_TO_HINT_FACTORY_ARGS_2: Dict[str, object] = {
    'builtins.dict': Dict,
    'collections.ChainMap': ChainMap,
}
'''
Dictionary mapping from the fully-qualified names of **dual-argument mapping
type hint factories** (i.e., standard Python types subscriptable by both key and
value child type hints and satisfying the :class:`collections.abc.Mapping`
protocol) to those factories.
'''
