#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
**Beartype Decidedly Object-Oriented Runtime-checking (DOOR) procedural
type hint inferrers** (i.e., high-level functions dynamically inferring the type
hints best describing arbitrary objects).
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    Deque,
    FrozenSet,
    KeysView,
    List,
    Set,
    Tuple,
    Type,
    ValuesView,
)
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

# ....................{ INFERRERS                          }....................
#FIXME: Unit test us up, please.
#FIXME: Memoize us up, please.
#FIXME: Docstring us up, please.
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
#(e.g., "list" subclasses). I sigh.
def infer_hint(
    obj: object,
    __beartype_obj_ids_seen__: FrozenSet[int] = frozenset(),
) -> object:

    hint: object = type(obj)

    if id(obj) in __beartype_obj_ids_seen__:
        hint = BeartypeHintInferrence.RECURSIVE
    elif isinstance(obj, type):
        hint = Type[obj]
    else:
        obj_classname = get_object_type_name(obj)
        hint_factory_args_1 = _CONTAINER_CLASSNAME_TO_HINT_FACTORY_ARGS_1.get(
            obj_classname)

        if hint_factory_args_1 is not None:
            hints_child = set()
            __beartype_obj_ids_seen__ |= {id(obj)}

            for item in obj:  # type: ignore[attr-defined]
                hint_child = infer_hint(
                    obj=item,
                    __beartype_obj_ids_seen__=__beartype_obj_ids_seen__,
                )
                hints_child.add(hint_child)

            hints_child_union = make_hint_pep484_union(tuple(hints_child))

            hint = (
                hint_factory_args_1[hints_child_union, ...]  # type: ignore[index]
                if hint_factory_args_1 is Tuple else
                hint_factory_args_1[hints_child_union]  # type: ignore[index]
            )

    return hint

# ....................{ PRIVATE ~ globals                  }....................
#FIXME: Shift into the "beartype._data.hint.pep" subpackage somewhere, please.
from beartype.typing import Dict
_CONTAINER_CLASSNAME_TO_HINT_FACTORY_ARGS_1: Dict[str, object] = {
    'builtins.dict_keys': KeysView,
    'builtins.dict_values': ValuesView,
    'builtins.frozenset': FrozenSet,
    'builtins.list': List,
    'builtins.set': Set,
    'builtins.tuple': Tuple,
    'collections.deque': Deque,
}
