#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright (c) 2014-2024 Beartype authors.
# See "LICENSE" for further details.

'''
Beartype **Decidedly Object-Oriented Runtime-checking (DOOR) procedural
collection items type hint inferrers** (i.e., high-level functions dynamically
inferring subscripted type hints that best describe pure-Python containers
containing one or more items).
'''

# ....................{ IMPORTS                            }....................
from beartype.typing import (
    Counter,
    Optional,
    Tuple,
)
from beartype._data.hint.datahinttyping import FrozenSetInts
from beartype._data.hint.pep.sign.datapepsignset import HINT_SIGNS_MAPPING
from beartype._util.hint.pep.proposal.utilpep484604 import (
    make_hint_pep484604_union)
from beartype._util.hint.pep.utilpepget import get_hint_pep_sign_or_none
from collections.abc import (
    Collection as CollectionABC,
    Mapping as MappingABC,
)

# ....................{ INFERERS                           }....................
#FIXME: Conditionally annotate tuples less than a certain fixed length (e.g., 10
#items) as fixed-length rather than variable-length tuple type hints. Yeah!
def infer_hint_collection_items(
    # Mandatory parameters.
    obj: CollectionABC,
    hint_factory: object,
    __beartype_obj_ids_seen__: FrozenSetInts,

    # Optional parameters.
    hint_sign_origin: Optional[object] = None,
) -> object:
    '''
    Type hint recursively validating the passed collection (including *all*
    items transitively reachable from this collection), defined by subscripting
    the passed type hint factory by the union of the child type hints validating
    these items.

    This function *cannot* be memoized, due to necessarily accepting the
    ``__beartype_obj_ids_seen__`` parameter unique to each call to the parent
    :func:`beartype.door.infer_hint` function.

    Parameters
    ----------
    obj : CollectionABC
        Collection to infer a type hint from.
    hint_factory : object
        Subscriptable type hint factory validating this collection (e.g., the
        :pep:`585`-compliant :class:`list` builtin type if this collection is a
        list).
    hint_sign_origin : Optional[object]
        **Hint sign origin** (i.e., type hint which, when passed to the
        :func:`beartype._util.hint.pep.utilpepget.get_hint_pep_sign_or_none`
        getter, returns the sign uniquely identifying this collection). Either:

        * If the sign uniquely identifying this collection derives from a type
          hint that differs from the sign uniquely identifying the passed type
          hint factory, the former.
        * Else, :data:`None`.

        Although the sign uniquely identifying the passed type hint factory
        typically suffices to identify this collection as well, counterexamples
        abound -- including:

        * :pep:`484`- and :pep:`585`-compliant **generic collections**. Consider
          a user-defined generic list ``class GenericList(list[T]): ...``. The
          sign uniquely identifying this generic when passed directly to the
          :func:`beartype._util.hint.pep.utilpepget.get_hint_pep_sign_or_none`
          getter is
          :data:`beartype._data.hint.pep.sign.datapepsigns.HintSignGeneric`.
          However, that sign yields no meaningful insights with respect to
          collection-specific type hint inference; instead, the sign uniquely
          identifying this generic *should* be
          :data:`beartype._data.hint.pep.sign.datapepsigns.HintSignList`. To
          support this discrepancy, a caller passing this generic as the ``obj``
          parameter to this function would also pass the erased
          pseudo-superclass ``list[T]`` as this ``hint_sign_origin`` parameter.
        * **Builtin collection subclasses**. Consider a user-defined builtin
          list subclass ``class ListSubclass(list): ...``. A similar
          justification applies.

        Defaults to :data:`None`, in which case this type hint defaults to the
        passed type hint factory.
    __beartype_obj_ids_seen__ : FrozenSet[int]
        **Recursion guard.** See also the parameter of the same name accepted by
        the :func:`beartype.door._func.infer.inferhint.infer_hint` function.

    Returns
    -------
    object
        Type hint inferred from the passed collection.

    Warns
    -----
    BeartypeDoorInferHintRecursionWarning
        On detecting that the passed iterable is **recursive** (i.e.,
        containing one or more items that self-referentially refer to this same
        iterable).
    '''
    assert isinstance(obj, CollectionABC), f'{repr(obj)} not collection.'
    assert isinstance(__beartype_obj_ids_seen__, frozenset), (
        f'{repr(__beartype_obj_ids_seen__)} not frozen set.')

    # ....................{ PREAMBLE                       }....................
    # If this collection is empty, return the this unsubscripted hint factory
    # permissively matching *ALL* collections of this type. Since *NO* child
    # type hints can be safely inferred from an empty collection, our only
    # recourse is to allow similar instances of this collection to contain *ALL*
    # possible items.
    if not obj:
        return hint_factory
    # Else, this collection is non-empty.

    # ....................{ LOCALS                         }....................
    # Add the integer uniquely identifying this collection to this set, thus
    # recording that this collection has now been visited by this recursion.
    __beartype_obj_ids_seen__ |= {id(obj)}

    # If passed *NO* hint sign origin, default this origin to the passed hint
    # factory.
    if hint_sign_origin is None:
        hint_sign_origin = hint_factory
    # Else, a hint sign origin. In this case, preserve this origin.

    # Sign uniquely identifying this collection.
    hint_sign = get_hint_pep_sign_or_none(hint_sign_origin)

    # Low-level private callable defined below suitable for inferring the full
    # type hint recursively validating this collection, defined as either...
    hint_inferer = (
        # If this collection is a mapping, the mapping-specific inferer;
        _infer_hint_mapping_items
        if hint_sign in HINT_SIGNS_MAPPING else
        # Else, this collection is *NOT* a mapping. In this case, the
        # general-purpose inferer applicable to *ALL* single-argument
        # reiterables (e.g., collections whose type hint factories are
        # subscriptable by only a single child type hint).
        _infer_hint_reiterable_items
    )

    # Type hint recursively validating this collection.
    hint = hint_inferer(
        obj=obj,  # type: ignore[arg-type]
        hint_factory=hint_factory,
        __beartype_obj_ids_seen__=__beartype_obj_ids_seen__,
    )

    # Return this hint.
    return hint

# ....................{ PRIVATE ~ inferers                 }....................
def _infer_hint_reiterable_items(
    obj: CollectionABC,
    hint_factory: object,
    __beartype_obj_ids_seen__: FrozenSetInts,
) -> object:
    '''
    Type hint recursively validating the passed **reiterable** (i.e.,
    collections whose type hint factories are subscriptable by only a single
    child type hint) and all items transitively reachable from this reiterable,
    defined by subscripting the passed type hint factory by the union of the
    child type hints validating these items.

    See Also
    --------
    :func:`.infer_hint_collection_items`
        Further details.
    '''

    # ....................{ IMPORTS                        }....................
    # Avoid circular import dependencies.
    from beartype.door._func.infer.inferhint import infer_hint

    # ....................{ LOCALS                         }....................
    # Set of all child type hints to conjoin into a union.
    hints_child = set()

    # ....................{ RECURSION                      }....................
    # For each item in this collection...
    for item in obj:
        # Child type hint validating this item.
        hint_child = infer_hint(
            obj=item, __beartype_obj_ids_seen__=__beartype_obj_ids_seen__)

        # Add this child type hint to this set.
        hints_child.add(hint_child)

    # ....................{ SUBSCRIPTION                   }....................
    # PEP 604- or 484-compliant union of these child type hints.
    hints_child_union = make_hint_pep484604_union(tuple(hints_child))

    # Type hint recursively validating this reiterable, defined by...
    hint = (
        # If this collection is a tuple, subscripting this tuple hint factory by
        # the variadic-length variant of this union followed by an ellipses
        # (signifying this tuple to contain arbitrarily many items);
        hint_factory[hints_child_union, ...]  # type: ignore[index]
        if hint_factory is Tuple else
        # Else, this collection is *NOT* a tuple. In this case, trivially
        # subscripting this non-tuple hint factory by this union.
        hint_factory[hints_child_union]  # type: ignore[index]
    )

    # Return this hint.
    return hint


def _infer_hint_mapping_items(
    obj: MappingABC,
    hint_factory: object,
    __beartype_obj_ids_seen__: FrozenSetInts,
) -> object:
    '''
    Type hint recursively validating the passed **mapping** (i.e.,
    collections whose type hint factories are subscriptable by a pair of child
    key and value type hints) and all keys *and* values transitively reachable
    from this mapping, defined by subscripting the passed type hint factory by
    the unions of the child type hints validating these keys and values.

    See Also
    --------
    :func:`.infer_hint_collection_items`
        Further details.
    '''
    assert isinstance(obj, MappingABC), f'{repr(obj)} not mapping.'

    # ....................{ IMPORTS                        }....................
    # Avoid circular import dependencies.
    from beartype.door._func.infer.inferhint import infer_hint

    # ....................{ LOCALS                         }....................
    # Set of all child key and value type hints to conjoin into a union.
    hints_key = set()
    hints_value = set()

    # ....................{ RECURSION                      }....................
    # For each key-value pair in this mapping...
    for key, value in obj.items():
        # Child key and value type hints validating this key and value.
        hint_key = infer_hint(
            obj=key, __beartype_obj_ids_seen__=__beartype_obj_ids_seen__)
        hint_value = infer_hint(
            obj=value, __beartype_obj_ids_seen__=__beartype_obj_ids_seen__)

        # Add this child type hint to this set.
        hints_key.add(hint_key)
        hints_value.add(hint_value)

    # ....................{ SUBSCRIPTION                   }....................
    # PEP 604- or 484-compliant union of these child key and value type hints.
    hints_key_union = make_hint_pep484604_union(tuple(hints_key))
    hints_value_union = make_hint_pep484604_union(tuple(hints_value))

    # Type hint recursively validating this mapping, defined as either...
    hint = (
        # If this mapping is a counter (i.e., instance of the standard
        # "collections.Counter" class), subscripting this factory by only this
        # key union. By definition, *ALL* values of *ALL* counters are
        # unconditionally constrained to be integers and thus need *NOT* (and
        # indeed *CANNOT*) be explicitly specified;
        hint_factory[hints_key_union]  # type: ignore[index]
        if hint_factory is Counter else
        # Else, this mapping is *NOT* a counter. In this case, sequentially
        # subscripting this factory by both this key and value union.
        hint_factory[hints_key_union, hints_value_union]  # type: ignore[index]
    )

    # Return this hint.
    return hint
