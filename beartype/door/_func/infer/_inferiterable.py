#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) procedural
container type hint inferrers** (i.e., high-level functions dynamically
inferring subscripted type hints that best describe pure-Python containers
containing one or more items).
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    FrozenSet,
    Tuple,
)
from beartype._data.hint.datahinttyping import FrozenSetInts
from beartype._util.hint.pep.proposal.utilpep484604 import (
    make_hint_pep484604_union)
from collections.abc import (
    Iterable as IterableABC,
)

# ....................{ INFERERS                           }....................
#FIXME: Conditionally annotate tuples less than a certain fixed length (e.g., 10
#items) as fixed-length rather than variable-length tuple type hints. Yeah!
#FIXME: Generalize to support user-defined subclasses of builtin container types
#(e.g., "list" subclasses). Note that doing so is complicated by Python 3.8,
#where those types are *NOT* subscriptable. Maybe ignore Python 3.8, honestly?
def infer_hint_iterable(
    iterable: IterableABC,
    hint_factory: object,
    __beartype_obj_ids_seen__: FrozenSetInts,
) -> object:
    '''
    Type hint recursively validating the passed iterable (including *all* items
    transitively reachable from this iterable), defined by subscripting the
    passed type hint factory by the union of the child type hints validating
    these items.

    Parameters
    ----------
    iterable : Iterable
        Pure-Python iterable to infer a type hint from.
    hint_factory : object
        Subscriptable type hint factory validating this iterable (e.g., the
        :class:`list` builtin if this iterable is a list).
    __beartype_obj_ids_seen__ : FrozenSet[int]
        **Recursion guard.** See also the parameter of the same name accepted by
        the :func:`beartype.door._func.infer.infermain.infer_hint` function.

    Returns
    -------
    object
        Type hint inferred from the passed iterable.

    Warns
    -----
    BeartypeDoorInferHintRecursionWarning
        On detecting that the passed iterable is **recursive** (i.e.,
        containing one or more items that self-referentially refer to this same
        iterable).
    '''
    assert isinstance(iterable, IterableABC), (
        f'{repr(iterable)} not iterable.')
    assert isinstance(__beartype_obj_ids_seen__, frozenset), (
        f'{repr(__beartype_obj_ids_seen__)} not frozen set.')

    # ....................{ IMPORTS                        }....................
    # Avoid circular import dependencies.
    from beartype.door._func.infer.infermain import infer_hint

    # ....................{ RECURSION                      }....................
    # Set of all child type hints to conjoin into a union.
    hints_child = set()

    # Add the integer uniquely identifying this collection to this set, thus
    # recording that this collection has now been visited by this recursion.
    __beartype_obj_ids_seen__ |= {id(iterable)}

    # For each item in this collection...
    for item in iterable:  # type: ignore[attr-defined]
        # Child type hint validating this item.
        hint_child = infer_hint(
            obj=item, __beartype_obj_ids_seen__=__beartype_obj_ids_seen__)

        # Add this child type hint to this set.
        hints_child.add(hint_child)

    # ....................{ RETURN                         }....................
    # PEP 604- or 484-compliant union of these child type hints.
    hints_child_union = make_hint_pep484604_union(tuple(hints_child))

    # Parent type hint recursively validating this collection (including
    # *ALL* items transitively reachable from this collection), defined by
    # subscripting this factory by this union.
    hint = (
        hint_factory[hints_child_union, ...]  # type: ignore[index]
        if hint_factory is Tuple else
        hint_factory[hints_child_union]  # type: ignore[index]
    )

    # Return this hint.
    return hint
