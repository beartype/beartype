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
from beartype._util.cache.utilcachecall import callable_cached
from beartype._util.hint.pep.proposal.pep484.utilpep484union import (
    make_hint_pep484_union)
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
#FIXME: Consider also adding support for standard "collections.abc" protocols.
#Doing so requires iterative isinstance()-based detection against a laundry list
#of such protocols. More sighing. *sigh*
#FIXME: Generalize to support user-defined subclasses of builtin container types
#(e.g., "list" subclasses). Note that doing so is complicated by Python 3.8,
#where those types are *NOT* subscriptable. I sigh.
@callable_cached
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

    This function is memoized for efficiency. Type hint inference thus exhibits:

    * Amortized :math:`O(1)` constant time complexity for even non-trivially
      complex pure-Python data structures, amortized across all calls to this
      function passed the same structures.
    * Worst-case :math:`O(n)` linear time complexity for the first call to this
      function passed a non-trivially complex pure-Python data structure, where
      :math:`n` is the number of objects transitively reachable from that
      structure.

    Caveats
    -------
    This function accepts **arbitrarily large pure-Python data structures.** To
    do so, this function necessarily introspects all objects reachable from
    those structures and thus exhibits worst-case :math:`O(n)` linear time
    complexity for the first call to this function passed such a structure.
    Unlike the remainder of :mod:`beartype`, this function does *not* guarantee
    non-amortized constant-time :math:`O(1)` behaviour by randomly sampling
    items from arbitrarily large pure-Python data structures. While feasible,
    doing so would be largely pointless. Why? Because a random sampling of items
    fails to yield completely accurate type hints. By definition, type hints are
    expected to be completely accurate. Inaccurate type hints are useless type
    hints, for all intents and purposes.

    This function accepts **recursive containers** (i.e., pure-Python containers
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

    Parameters
    ----------
    obj : object
        Arbitrary object to infer a type hint from.

    Returns
    -------
    object
        Type hint inferred from the passed object.
    '''

    # Defer to the memoized implementation of this function.
    #
    # Note that this function itself is intentionally *NOT* memoized. Why?
    # Keyword parameters. Efficiency is the entire point of memoization. But
    # keyword parameters are *MUCH* less efficient than positional parameters.
    # Ergo, the @callable_cached prohibits keyword parameters. However, keyword
    # parameters are also *MUCH* more usable, readable, and debuggable than
    # positional parameters. Ergo, this function *MUST* accept keyword
    # parameters. To resolve this dichotomy:
    # * This high-level public unmemoized function accepts keyword parameters
    #   and then passes those parameters on to...
    # * The lower-level private memoized _infer_hint_cached() function, which
    #   prohibits keyword parameters.
    return _infer_hint_cached(obj)

# ....................{ PRIVATE ~ inferers                 }....................
@callable_cached
def _infer_hint_cached(
    # Mandatory parameters.
    obj: object,

    # Hidden parameters. *GULP*
    __beartype_obj_ids_seen__: FrozenSet[int] = frozenset(),
) -> object:
    '''
    Type hint annotating the passed object.

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

    See Also
    --------
    :func:`.infer_hint`
        Further details.
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
    # satisfying this object if any *OR* "None" otherwise (i.e., if no such
    # factory satisfies this object).
    hint_factory_args_1 = _COLLECTION_CLASSNAME_TO_HINT_FACTORY_ARGS_1.get(
        obj_classname)

    # If a single-argument collection type hint factory satisfies this object,
    # this object is a collection of zero or more items. In this case...
    if hint_factory_args_1 is not None:
        # Add the integer uniquely identifying this collection to this set to
        # note that this collection has now been visited by this recursion.
        __beartype_obj_ids_seen__ |= {id(obj)}

        # Set of all child type hints to conjoin into a union.
        hints_child = set()

        # For each item in this collection...
        for item in obj:  # type: ignore[attr-defined]
            # Child type hint satisfying this item.
            hint_child = _infer_hint_cached(item, __beartype_obj_ids_seen__)

            # Add this child type hint to this set.
            hints_child.add(hint_child)

        #FIXME: Refactor as follows, please:
        #* Define a new make_hint_pep484604_union() factory.
        #* Call that factory here instead.
        # PEP 484- or 604-compliant union of these child type hints.
        hints_child_union = make_hint_pep484_union(tuple(hints_child))

        hint = (
            hint_factory_args_1[hints_child_union, ...]  # type: ignore[index]
            if hint_factory_args_1 is Tuple else
            hint_factory_args_1[hints_child_union]  # type: ignore[index]
        )

        return hint
    # Else, no such factory satisfies this object.

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
#* "ChainMap".
#* "Counter".
_MAPPING_CLASSNAME_TO_HINT_FACTORY_ARGS_2: Dict[str, object] = {
    'builtins.dict': Dict,
}
'''
Dictionary mapping from the fully-qualified names of **dual-argument mapping
type hint factories** (i.e., standard Python types subscriptable by both key and
value child type hints and satisfying the :class:`collections.abc.Mapping`
protocol) to those factories.
'''
